import os
import shutil
import json
import base64
import sqlite3
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from core_auditor import run_audit_task
from utils_html import generate_html_screenshot

app = FastAPI()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保目录存在
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "designs")
os.makedirs(UPLOAD_DIR, exist_ok=True)
DB_PATH = os.path.join(BASE_DIR, "audit_system.db")

# 挂载静态文件用于预览
app.mount("/uploads", StaticFiles(directory=os.path.join(BASE_DIR, "uploads")), name="uploads")

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".pdf", ".html"}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        avatar TEXT DEFAULT ''
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS user_configs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        baseline_config TEXT,
        design_config TEXT,
        component_config TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS audit_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        url TEXT,
        mode TEXT,
        score INTEGER,
        issue_count INTEGER,
        report_data TEXT,
        created_at TEXT
    )""")
    conn.commit()
    conn.close()
    print("Database initialized.")

init_db()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- 用户认证相关 ---
class UserAuth(BaseModel):
    username: str
    password: str

@app.post("/api/register")
async def register(user: UserAuth):
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user.username, user.password))
        db.commit()
        return {"status": "success", "message": "注册成功"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="用户名已存在")
    finally:
        db.close()

@app.post("/api/login")
async def login(user: UserAuth):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (user.username, user.password))
    row = cursor.fetchone()
    db.close()
    if row:
        return {"status": "success", "data": dict(row)}
    else:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

@app.get("/api/user/{user_id}")
async def get_user(user_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, username, avatar FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    db.close()
    if row:
        return {"status": "success", "data": dict(row)}
    raise HTTPException(status_code=404, detail="用户不存在")

@app.post("/api/update_password")
async def update_password(req: dict):
    user_id = req.get("user_id")
    new_pwd = req.get("new_password")
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_pwd, user_id))
    db.commit()
    db.close()
    return {"status": "success"}

@app.post("/api/update_avatar")
async def update_avatar(req: dict):
    user_id = req.get("user_id")
    avatar = req.get("avatar")
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE users SET avatar = ? WHERE id = ?", (avatar, user_id))
    db.commit()
    db.close()
    return {"status": "success"}

# --- 配置管理 ---
@app.get("/api/config/{user_id}")
async def get_config(user_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user_configs WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    db.close()
    if row:
        return {
            "status": "success", 
            "data": {
                "baseline_config": json.loads(row["baseline_config"]) if row["baseline_config"] else None,
                "design_config": json.loads(row["design_config"]) if row["design_config"] else None,
                "component_config": json.loads(row["component_config"]) if row["component_config"] else None
            }
        }
    return {"status": "success", "data": None}

@app.post("/api/config")
async def save_config(req: dict):
    user_id = req.get("user_id")
    # 支持单模式更新或全量更新
    mode = req.get("mode") # baseline, design, component
    
    db = get_db()
    cursor = db.cursor()
    
    # 确保用户记录存在
    cursor.execute("SELECT 1 FROM user_configs WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO user_configs (user_id) VALUES (?)", (user_id,))
    
    if mode:
        # 单模式更新逻辑 (旧逻辑兼容)
        field = f"{mode}_config"
        config_data = json.dumps(req.get("config"))
        cursor.execute(f"UPDATE user_configs SET {field} = ? WHERE user_id = ?", (config_data, user_id))
    else:
        # 全量更新逻辑 (新版 Config.vue 发出的格式)
        if "baseline_config" in req:
            cursor.execute("UPDATE user_configs SET baseline_config = ? WHERE user_id = ?", 
                           (json.dumps(req["baseline_config"]), user_id))
        if "design_config" in req:
            cursor.execute("UPDATE user_configs SET design_config = ? WHERE user_id = ?", 
                           (json.dumps(req["design_config"]), user_id))
        if "component_config" in req:
            cursor.execute("UPDATE user_configs SET component_config = ? WHERE user_id = ?", 
                           (json.dumps(req["component_config"]), user_id))
    
    db.commit()
    db.close()
    return {"status": "success"}

# --- 走查任务 ---
@app.post("/api/design/upload")
async def upload_design(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式: {ext}")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    safe_name = f"{timestamp}{ext}"
    dest = os.path.join(UPLOAD_DIR, safe_name)

    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    file_url = f"/uploads/designs/{safe_name}"
    file_type = "image" if ext in {".png", ".jpg", ".jpeg", ".svg"} else ext.lstrip(".")
    
    preview_url = file_url
    if ext == ".html":
        try:
            png_path = await generate_html_screenshot(dest)
            preview_url = f"/uploads/designs/{os.path.basename(png_path)}"
        except Exception as e:
            print(f"HTML 截图生成失败: {e}")

    return {
        "status": "success",
        "data": {
            "file_id": safe_name,
            "file_name": file.filename,
            "file_url": file_url,
            "preview_url": preview_url,
            "file_path": f"uploads/designs/{safe_name}",
            "file_type": file_type
        }
    }

class AuditReq(BaseModel):
    url: str
    config: Dict[str, Any]
    mode: str
    user_id: Optional[int] = None

class DeleteHistoryReq(BaseModel):
    user_id: int
    ids: List[int]

@app.post("/api/audit")
@app.post("/api/audit/run")
async def run_audit(req: AuditReq):
    try:
        # 调用核心审计逻辑
        result = await run_audit_task(req.url, req.config, req.mode)
        
        # 存入历史记录
        if req.user_id:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO audit_history (user_id, url, mode, score, issue_count, report_data, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                req.user_id, req.url, req.mode, result["score"], result["issueCount"], 
                json.dumps(result), datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            db.commit()
            db.close()
            
        return {"status": "success", "data": result}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@app.get("/api/history/{user_id}")
async def get_history(user_id: int):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM audit_history WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    rows = cursor.fetchall()
    db.close()
    
    history = []
    for row in rows:
        item = dict(row)
        item["report_data"] = json.loads(item["report_data"])
        history.append(item)
    return {"status": "success", "data": history}

@app.post("/api/history/delete")
async def delete_history(req: DeleteHistoryReq):
    if not req.ids:
        raise HTTPException(status_code=400, detail="请至少选择一条历史记录")

    db = get_db()
    cursor = db.cursor()
    placeholders = ",".join(["?"] * len(req.ids))
    params = [req.user_id] + req.ids
    cursor.execute(
        f"DELETE FROM audit_history WHERE user_id = ? AND id IN ({placeholders})",
        params
    )
    deleted_count = cursor.rowcount
    db.commit()
    db.close()
    return {"status": "success", "deleted_count": deleted_count}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
