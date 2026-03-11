from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
import sqlite3
import json
from datetime import datetime
from core_auditor import run_audit_task

app = FastAPI(title="UI Audit API")

# 配置跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 1. 数据库初始化
# ==========================================
def init_db():
    conn = sqlite3.connect('audit_system.db')
    c = conn.cursor()
    # 创建用户表
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, avatar TEXT)''')
    # 创建历史记录表
    c.execute('''CREATE TABLE IF NOT EXISTS audit_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, url TEXT, mode TEXT, 
                  score INTEGER, issue_count INTEGER, report_data TEXT, created_at TEXT)''')
    
    # 插入一个默认测试账号 (如果不存在的话)
    c.execute("INSERT OR IGNORE INTO users (username, password, avatar) VALUES ('admin', '123456', 'PM')")
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 2. 数据请求模型 (Pydantic Models)
# ==========================================
class LoginReq(BaseModel):
    username: str
    password: str

class RegisterReq(BaseModel):
    username: str
    password: str

class UpdateAvatarReq(BaseModel):
    user_id: int
    avatar: str

class UpdatePwdReq(BaseModel):
    user_id: int
    old_password: str
    new_password: str

class AuditReq(BaseModel):
    url: str
    mode: str
    config: Dict[str, Any]
    user_id: int

# ==========================================
# 3. API 接口定义
# ==========================================

# --- 登录 ---
@app.post("/api/login")
async def login(req: LoginReq):
    conn = sqlite3.connect('audit_system.db')
    c = conn.cursor()
    c.execute("SELECT id, username, avatar FROM users WHERE username=? AND password=?", (req.username, req.password))
    user = c.fetchone()
    conn.close()
    if user:
        return {"status": "success", "data": {"id": user[0], "username": user[1], "avatar": user[2]}}
    raise HTTPException(status_code=401, detail="用户名或密码错误")

# --- 注册 ---
@app.post("/api/register")
async def register(req: RegisterReq):
    conn = sqlite3.connect('audit_system.db')
    c = conn.cursor()
    try:
        # 默认给新用户一个头像，取用户名的首字母大写
        default_avatar = req.username[0].upper() if req.username else "U"
        c.execute("INSERT INTO users (username, password, avatar) VALUES (?, ?, ?)", 
                  (req.username, req.password, default_avatar))
        conn.commit()
        return {"status": "success", "message": "注册成功"}
    except sqlite3.IntegrityError:
        return {"status": "error", "message": "用户名已存在"}
    finally:
        conn.close()

# --- 修改头像 ---
@app.post("/api/update_avatar")
async def update_avatar(req: UpdateAvatarReq):
    conn = sqlite3.connect('audit_system.db')
    c = conn.cursor()
    c.execute("UPDATE users SET avatar=? WHERE id=?", (req.avatar, req.user_id))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "头像更新成功"}

# --- 修改密码 ---
@app.post("/api/update_password")
async def update_password(req: UpdatePwdReq):
    conn = sqlite3.connect('audit_system.db')
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE id=? AND password=?", (req.user_id, req.old_password))
    if not c.fetchone():
        conn.close()
        return {"status": "error", "message": "原密码错误"}
    
    c.execute("UPDATE users SET password=? WHERE id=?", (req.new_password, req.user_id))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "密码修改成功"}

# --- 发起走查 ---
@app.post("/api/audit")
async def start_audit(req: AuditReq):
    try:
        # 1. 运行核心走查与 AI 分析
        result = await run_audit_task(req.url, req.config, req.mode)
        
        # 2. 存入真实数据库
        conn = sqlite3.connect('audit_system.db')
        c = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        c.execute("""INSERT INTO audit_history (user_id, url, mode, score, issue_count, report_data, created_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                  (req.user_id, req.url, req.mode, result.get("score", 0), result.get("issueCount", 0), json.dumps(result), now))
        record_id = c.lastrowid
        conn.commit()
        conn.close()
        
        result["id"] = record_id # 返回记录ID
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- 获取历史记录 ---
@app.get("/api/history/{user_id}")
async def get_history(user_id: int):
    conn = sqlite3.connect('audit_system.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, url, mode, score, issue_count, created_at, report_data FROM audit_history WHERE user_id=? ORDER BY id DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    
    history_list = [dict(row) for row in rows]
    return {"status": "success", "data": history_list}


if __name__ == "__main__":
    # 启动 Uvicorn 服务
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)