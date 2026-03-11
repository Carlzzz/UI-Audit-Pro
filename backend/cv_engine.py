import cv2
import numpy as np

# 🚨 新增 config 参数
def compute_visual_diff(web_bytes: bytes, figma_bytes: bytes, config: dict):
    print("🤖 正在启动 OpenCV 智能感知比对引擎...")

    web_img = cv2.imdecode(np.frombuffer(web_bytes, np.uint8), cv2.IMREAD_COLOR)
    figma_img = cv2.imdecode(np.frombuffer(figma_bytes, np.uint8), cv2.IMREAD_COLOR)

    h1, w1 = web_img.shape[:2]
    h2, w2 = figma_img.shape[:2]
    min_h, min_w = min(h1, h2), min(w1, w2)
    
    web_crop = web_img[:min_h, :min_w]
    figma_crop = figma_img[:min_h, :min_w]

    # 🟢 1. 挂载配置：忽略区域 (Ignore Regions)
    # 如果前端配置了忽略状态栏 (通常高度为 40px)
    if config.get('ignoreStatus', True):
        print("🛡️ 已应用遮罩：忽略顶部状态栏")
        web_crop[0:40, :] = 0
        figma_crop[0:40, :] = 0

    web_gray = cv2.cvtColor(web_crop, cv2.COLOR_BGR2GRAY)
    figma_gray = cv2.cvtColor(figma_crop, cv2.COLOR_BGR2GRAY)

    web_blur = cv2.GaussianBlur(web_gray, (5, 5), 0)
    figma_blur = cv2.GaussianBlur(figma_gray, (5, 5), 0)

    diff = cv2.absdiff(web_blur, figma_blur)

    # 🟢 2. 挂载配置：色差容忍度 (Color Threshold)
    # 前端传来的是 0-100 的百分比，0最严格，100最宽松。
    # 转化为 OpenCV 255 色阶的阈值 (默认 10% 对应约 25 的色阶容差)
    user_threshold_pct = config.get('colorThreshold', 10)
    # 确保最小有一定的容差防止抗锯齿报错，最大不超过 100
    cv_thresh_value = max(15, int((user_threshold_pct / 100.0) * 255))
    
    print(f"🎚️ 应用动态色差容忍阈值: {user_threshold_pct}% -> CV2 Value: {cv_thresh_value}")
    
    _, thresh = cv2.threshold(diff, cv_thresh_value, 255, cv2.THRESH_BINARY)

    kernel = np.ones((15, 15), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=2)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    issues = []
    issue_id = 1
    
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        # 过滤极小噪点
        if w > 15 and h > 15:
            issues.append({
                "id": issue_id,
                "title": "设计稿视觉偏差",
                "level": "warning" if (w < 50 or h < 50) else "high",
                "category": "像素级对比",
                "desc": f"发现 {w}x{h}px 的视觉差异区域",
                "suggestion": "请参照 Figma 修正此处间距或组件样式",
                "rect": {"top": y, "left": x, "width": w, "height": h}
            })
            issue_id += 1

    return issues