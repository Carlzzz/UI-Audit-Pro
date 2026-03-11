import json
import base64
from playwright.async_api import async_playwright
from ai_service import generate_diagnosis
from figma_service import fetch_figma_image
from cv_engine import compute_visual_diff


# 注意这里新增了 mode 参数
async def run_audit_task(url: str, config: dict, mode: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 强制锁定 1440 视口，保证与设计稿对齐
        context = await browser.new_context(viewport={'width': 1440, 'height': 1080})
        page = await context.new_page()

        try:
            # 🚨 核心修复 1：把 networkidle 改为 domcontentloaded，防止无休止的等待和跳转销毁上下文
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_timeout(2000) # 给动态渲染一点时间
        except Exception as e:
            print(f"页面加载超时或跳转(可忽略): {e}")

        # 🚨 核心修复 2：加入 try-except 防弹装甲。即使上下文被销毁，也不会导致 500 崩溃
        try:
            await page.add_style_tag(content="""
                ::-webkit-scrollbar { display: none !important; }
                * { scrollbar-width: none !important; }
            """)
            await page.evaluate("window.scrollTo(0, 0)")
            await page.evaluate("document.fonts.ready")
            await page.wait_for_timeout(1000)
        except Exception as e:
            print(f"样式注入警告(页面可能发生了重定向，继续执行): {e}")

        # 📸 无论是哪种模式，先截取前端真实网页的全屏图
        screenshot_bytes = await page.screenshot(type='png', full_page=True)
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')

        # ===============================================
        # 🟢 模式 A：设计稿像素级对比模式 (OpenCV)
        # ===============================================
        if mode == "design":
            await browser.close()
            
            figma_bytes = None
            local_b64 = config.get("localImageBase64")
            figma_url = config.get("url")
            
            try:
                # 1. 优先检查：是否有本地上传的 Base64 图片
                if local_b64:
                    print("📂 检测到本地上传的设计稿资源，正在解码...")
                    figma_bytes = base64.b64decode(local_b64)
                
                # 2. 其次检查：是否有 Figma 链接
                elif figma_url:
                    figma_bytes = fetch_figma_image(figma_url)
                
                # 3. 都没有则抛出明确错误
                else:
                    raise ValueError("未提供 Figma 链接或本地设计稿图片！请在页面中配置资源。")

                # 启动 CV 引擎比对
                issues = compute_visual_diff(screenshot_bytes, figma_bytes, config)
                
            except Exception as e:
                issues = [{
                    "id": 999, "title": "设计稿解析失败", "level": "high", "category": "系统报错",
                    "desc": str(e), "suggestion": "请检查 Figma 链接/Token，或确保本地图片格式正确（支持 PNG/JPG）", 
                    "rect": {"top": 100, "left": 100, "width": 400, "height": 100}
                }]
                
        # ===============================================
        # 🔵 模式 B：基准值 DOM 走查模式 (JS AST)
        # ===============================================
        else:
            # 🚨 终极基准规则引擎：全面读取 Config 新参数
            js_auditor = """
            (config) => {
                window.scrollTo(0, 0);
                const issues = [];
                let issueId = 1;
                
                // 1. 读取前端传入的动态配置 (完美映射新版 UI)
                const allowedFonts = config.fontTokens && config.fontTokens.length > 0 ? config.fontTokens : [12, 14, 16, 18, 20, 24, 32];
                const allowedRadius = config.radiusTokens || [2, 4, 8, 12, 16];
                const minClickArea = config.minClickArea || 44;
                const altCheck = config.altCheck !== false; 
                const webpCheck = config.webpCheck !== false;
                const colorTolerance = config.colorTolerance || 15; // 色差容忍阈值
                
                const brandColors = (config.colors || []).map(c => {
                    const hex = c.hex.replace('#', '');
                    return {
                        r: parseInt(hex.substring(0, 2), 16) || 0,
                        g: parseInt(hex.substring(2, 4), 16) || 0,
                        b: parseInt(hex.substring(4, 6), 16) || 0,
                        label: c.label
                    };
                });

                const colorDistance = (rgb1, rgb2) => Math.sqrt(Math.pow(rgb1.r - rgb2.r, 2) + Math.pow(rgb1.g - rgb2.g, 2) + Math.pow(rgb1.b - rgb2.b, 2));

                const els = document.querySelectorAll('button, a, p, h1, h2, h3, img, span, div.card');

                Array.from(els).forEach((el) => {
                    const tag = el.tagName.toLowerCase();
                    const style = window.getComputedStyle(el);
                    
                    let rect;
                    if (['h1','h2','h3','p','a','span'].includes(tag) && el.innerText.trim().length > 0) {
                        const range = document.createRange();
                        const textNode = Array.from(el.childNodes).find(n => n.nodeType === Node.TEXT_NODE && n.textContent.trim().length > 0);
                        if (textNode) { range.selectNode(textNode); rect = range.getBoundingClientRect(); }
                        else { rect = el.getBoundingClientRect(); }
                    } else { rect = el.getBoundingClientRect(); }
                    
                    if (!rect || rect.width <= 2 || rect.height <= 2 || rect.width > 900) return;
                    const cords = { top: rect.top + window.scrollY, left: rect.left + window.scrollX, width: rect.width, height: rect.height };

                    // 🔴 检查 1：最小点击热区
                    if (['button', 'a'].includes(tag)) {
                        if (rect.width < minClickArea || rect.height < minClickArea) {
                            issues.push({ id: issueId++, title: "热区过小", level: "high", category: "交互", desc: `实测 ${Math.round(rect.width)}x${Math.round(rect.height)}px`, suggestion: `建议长宽均大于规范的 ${minClickArea}px`, rect: cords });
                        }
                    }

                    // 🔴 检查 2：品牌色近色污染检测
                    if (config.nearColorCheck && brandColors.length > 0) {
                        const bgMatch = style.backgroundColor.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/);
                        if (bgMatch) {
                            const bgRgb = { r: parseInt(bgMatch[1]), g: parseInt(bgMatch[2]), b: parseInt(bgMatch[3]) };
                            if (!(bgRgb.r > 250 && bgRgb.g > 250 && bgRgb.b > 250) && bgRgb.r !== 0 && style.backgroundColor !== 'rgba(0, 0, 0, 0)') {
                                let nearestDist = 999;
                                let nearestBrand = null;
                                brandColors.forEach(bc => {
                                    const dist = colorDistance(bgRgb, bc);
                                    if (dist < nearestDist) { nearestDist = dist; nearestBrand = bc; }
                                });
                                // 容忍度算法：距离大于容忍阈值，但小于污染极值，视为近色污染
                                if (nearestDist > colorTolerance && nearestDist < colorTolerance + 50) {
                                    issues.push({ id: issueId++, title: "品牌色偏离", level: "warning", category: "色彩", desc: `背景色存在细微污染(差值:${Math.round(nearestDist)})`, suggestion: `建议统一替换为: ${nearestBrand.label}`, rect: cords });
                                }
                            }
                        }
                    }

                    // 🔴 检查 3：允许的字阶校验
                    if (['h1', 'h2', 'h3', 'p', 'a', 'button'].includes(tag) && el.innerText.trim().length > 0) {
                        const fs = parseFloat(style.fontSize);
                        if (allowedFonts.length > 0 && !allowedFonts.includes(fs)) {
                            issues.push({ id: issueId++, title: "字号异常", level: "high", category: "排版", desc: `实测 ${fs}px，不在白名单内`, suggestion: `请修改为字阶 Token: ${allowedFonts.join(', ')}`, rect: cords });
                        }
                    }

                    // 🔴 检查 4：无障碍与图片合规
                    if (tag === 'img') {
                        if (altCheck && (!el.hasAttribute('alt') || el.getAttribute('alt').trim() === '')) {
                            issues.push({ id: issueId++, title: "无障碍缺失", level: "high", category: "合规", desc: `Img 缺失 alt 属性`, suggestion: `按 W3C 标准添加替代文本`, rect: cords });
                        }
                        if (webpCheck && el.src) {
                            const ext = el.src.split('.').pop().toLowerCase();
                            if (['png', 'jpg', 'jpeg'].includes(ext)) {
                                issues.push({ id: issueId++, title: "图片未优化", level: "warning", category: "性能", desc: `使用了传统 ${ext} 格式`, suggestion: `建议转换为 WebP 以提升性能`, rect: cords });
                            }
                        }
                    }
                });

                return issues;
            }
            """
            issues = await page.evaluate(js_auditor, config)
            await browser.close()

        # 生成 AI 诊断总结
        diagnosis = await generate_diagnosis(issues)
        issue_count = len(issues)
        score = max(0, 100 - (issue_count * 5))

        return {
            "score": score,
            "compliance": max(0, 100 - (issue_count * 3)),
            "issueCount": issue_count,
            "issues": issues,
            "diagnosis": diagnosis,
            "screenshot": screenshot_base64,
            "url": url,
            "mode": mode # 记录当前使用的模式
        }