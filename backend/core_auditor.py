from static_scanner import run_static_scan
import json
import base64
import os
from playwright.async_api import async_playwright
from ai_service import generate_diagnosis
# from figma_service import fetch_figma_image
from cv_engine import compute_visual_diff


def _non_empty_list(v) -> bool:
    return isinstance(v, list) and len(v) > 0


def _merge_baseline_token_lists(config: dict, camel: str, snake: str) -> None:
    """camel 与 snake 同时存在时合并去重；camel 为空列表时采用 snake，避免默认 spacingTokens 盖住已保存的 spacing_tokens。"""
    if not isinstance(config, dict):
        return
    a = config.get(camel)
    b = config.get(snake)
    if not _non_empty_list(b):
        return
    if not _non_empty_list(a):
        config[camel] = list(b)
        return
    seen = set()
    out = []
    for x in a + b:
        if x is None:
            continue
        k = str(x).strip()
        if not k or k in seen:
            continue
        seen.add(k)
        out.append(x)
    config[camel] = out


def _normalize_baseline_config_keys(config: dict) -> None:
    """前端或存储层可能使用 snake_case；走查脚本与前端字段对齐为 camelCase。"""
    if not isinstance(config, dict):
        return
    for camel, snake in (
        ("spacingTokens", "spacing_tokens"),
        ("gridTokens", "grid_tokens"),
        ("radiusTokens", "radius_tokens"),
        ("buttonHeightTokens", "button_height_tokens"),
        ("inputHeightTokens", "input_height_tokens"),
        ("buttonHeightCheck", "button_height_check"),
        ("inputSelectHeightCheck", "input_select_height_check"),
        ("gridCheck", "grid_check"),
        ("radiusCheck", "radius_check"),
    ):
        if snake in config and camel not in config:
            config[camel] = config[snake]
    _merge_baseline_token_lists(config, "spacingTokens", "spacing_tokens")
    _merge_baseline_token_lists(config, "gridTokens", "grid_tokens")
    _merge_baseline_token_lists(config, "radiusTokens", "radius_tokens")


# 注意这里新增了 mode 参数
async def run_audit_task(url: str, config: dict, mode: str):
    # 🌟 新增：检测是否为本地路径进行静态扫描
    is_local_file = os.path.exists(url) or url.startswith('/') or (':' in url and not url.startswith('http') and not url.startswith('data'))
    
    if is_local_file:
        print(f"🔍 检测到本地路径，切换至静态扫描模式: {url}")
        issues = run_static_scan(url, config)
        # 静态扫描无截图
        screenshot_base64 = ""
        
        # 生成 AI 诊断总结
        diagnosis = await generate_diagnosis(issues)
        
        high_count = len([i for i in issues if i.get('level') == 'high'])
        medium_count = len([i for i in issues if i.get('level') == 'medium'])
        low_count = len([i for i in issues if i.get('level') == 'low' or i.get('level') == 'warning'])
        issue_count = len(issues)
        
        score = max(0, 100 - (high_count * 8 + medium_count * 3 + low_count * 1))
        compliance = max(0, 100 - (high_count * 10 + medium_count * 4 + low_count * 1))

        return {
            "score": score,
            "compliance": compliance,
            "issueCount": issue_count,
            "issues": issues,
            "diagnosis": diagnosis,
            "screenshot": screenshot_base64,
            "url": url,
            "mode": "static_scan"
        }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 强制锁定 1440 视口，保证与设计稿对齐
        context_args = {'viewport': {'width': 1440, 'height': 1080}}
        
        # 处理授权注入 (Headers / Cookie)
        custom_headers = {}
        if config.get("authHeader"):
            # 支持直接填入 Bearer xxxx 格式
            custom_headers["Authorization"] = config.get("authHeader")
        if config.get("cookieStr"):
            custom_headers["Cookie"] = config.get("cookieStr")
            
        if custom_headers:
            context_args['extra_http_headers'] = custom_headers

        context = await browser.new_context(**context_args)
        
        # 注入 LocalStorage (如果有的话)
        if config.get("localStorageStr"):
            try:
                ls_data = json.loads(config.get("localStorageStr"))
                js_code = "try {\n"
                for k, v in ls_data.items():
                    js_code += f"localStorage.setItem('{k}', '{v}');\n"
                js_code += "} catch(e) {}"
                await context.add_init_script(js_code)
            except Exception as e:
                print(f"LocalStorage 解析失败: {e}")

        page = await context.new_page()

        try:
            # 🚨 核心修复 1：把 networkidle 改为 domcontentloaded，防止无休止的等待和跳转销毁上下文
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_timeout(2000) # 给动态渲染一点时间
            
            # === 新增：通用账号密码自动登录逻辑 ===
            if config.get("loginUser") and config.get("loginPwd"):
                print("🔄 检测到账号密码配置，尝试执行自动化登录...")
                try:
                    # 尝试匹配常见的账号输入框
                    user_input = page.locator("input[name*='user'], input[name*='account'], input[type='text']").first
                    if await user_input.count() > 0:
                        await user_input.fill(config.get("loginUser"))
                    
                    # 尝试匹配常见的密码输入框
                    pwd_input = page.locator("input[type='password']").first
                    if await pwd_input.count() > 0:
                        await pwd_input.fill(config.get("loginPwd"))
                    
                    # 尝试匹配常见的登录按钮
                    submit_btn = page.locator("button[type='submit'], button:has-text('登录'), button:has-text('Login'), .login-btn").first
                    if await submit_btn.count() > 0:
                        await submit_btn.click()
                        await page.wait_for_timeout(4000) # 等待登录跳转和渲染完成
                        print("✅ 自动化登录交互执行完毕")
                except Exception as le:
                    print(f"⚠️ 自动化登录失败: {le}")
                    
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
            uploaded_file = config.get("uploadedFile")
            local_b64 = config.get("localImageBase64")
            
            try:
                # 1. 优先检查：是否有新版上传的文件
                if uploaded_file and (uploaded_file.get("file_id") or uploaded_file.get("file_path")):
                    # 尝试从 file_id 或 file_path 获取文件名
                    file_name = uploaded_file.get("file_id") or os.path.basename(uploaded_file.get("file_path"))
                    file_path = os.path.join(os.path.dirname(__file__), "uploads", "designs", file_name)
                    
                    print(f"📂 正在加载上传的设计稿: {file_path}")
                    if not os.path.exists(file_path):
                        raise FileNotFoundError(f"设计稿文件不存在: {file_path}")
                    
                    # 🌟 处理 HTML 设计稿：自动切换到生成的 PNG 进行 CV 对比
                    if file_path.lower().endswith('.html'):
                        png_path = file_path + ".png"
                        if not os.path.exists(png_path):
                            from utils_html import generate_html_screenshot
                            print("🔄 正在实时生成 HTML 设计稿截图...")
                            await generate_html_screenshot(file_path)
                        file_path = png_path
                        print(f"🖼️ 使用 HTML 渲染后的截图进行比对: {file_path}")
                        
                    with open(file_path, "rb") as f:
                        figma_bytes = f.read()
                
                # 2. 其次检查：旧版 Base64
                elif local_b64:
                    print("📂 检测到本地上传的设计稿资源，正在解码...")
                    figma_bytes = base64.b64decode(local_b64)
                
                # 3. 都没有则抛出明确错误
                else:
                    raise ValueError("未提供设计稿图片资源！请在走查配置页面上传文件。")

                # 启动 CV 引擎比对
                issues = compute_visual_diff(screenshot_bytes, figma_bytes, config)
                
            except Exception as e:
                issues = [{
                    "id": 999, "title": "设计稿解析失败", "level": "high", "category": "系统报错",
                    "desc": str(e), "suggestion": "请重新上传设计稿，并确保图片格式正确（支持 PNG/JPG）", 
                    "rect": {"top": 100, "left": 100, "width": 400, "height": 100}
                }]
                
        # ===============================================
        # 🟠 模式 C：组件模式 (基于组件级规则库)
        # ===============================================
        elif mode == "component":
            # JS 注入：专门针对组件的走查逻辑 (深度对接 Config 全量规则)
            js_auditor = """
(config) => {
    window.scrollTo(0, 0);
    const issues = [];
    let issueId = 1;

    // --- Helper functions ---
    const coercePx = (v) => {
        if (v == null || v === '') return NaN;
        const s = String(v).trim().replace(/px$/i, '').trim();
        const n = parseFloat(s);
        return (Number.isFinite(n) && n > 0) ? n : NaN;
    };
    const parseTokens = (val) => {
        if (!val) return [];
        if (Array.isArray(val)) return [...new Set(val.map(coercePx).filter(n => !Number.isNaN(n)).map(n => Math.round(n)))];
        if (typeof val === 'string') return [...new Set(val.split(',').map(s => coercePx(s.trim())).filter(n => !Number.isNaN(n)).map(n => Math.round(n)))];
        return [];
    };
    const matchesToken = (value, tokens, tolerance = 0.5) =>
        tokens.some(token => Math.abs(value - token) <= tolerance);
    const isMultipleOfAnyPx = (val, bases) => {
        const vf = Number(val);
        if (Number.isNaN(vf) || vf <= 0) return true;
        if (!bases || bases.length === 0) return true;
        const v = Math.round(vf);
        return bases.some((base) => {
            const b = Math.round(Number(base));
            if (Number.isNaN(b) || b <= 0) return false;
            return (v % b + b) % b === 0;
        });
    };

    const hexToRgb = (hex) => {
        if (!hex) return { r:0, g:0, b:0 };
        const h = hex.replace('#', '');
        return { r: parseInt(h.substring(0,2),16)||0, g: parseInt(h.substring(2,4),16)||0, b: parseInt(h.substring(4,6),16)||0 };
    };

    const colorDist = (a, b) => Math.sqrt(Math.pow(a.r-b.r,2)+Math.pow(a.g-b.g,2)+Math.pow(a.b-b.b,2));

    const parseRgbStr = (s) => {
        if (!s) return null;
        const m = s.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/);
        return m ? { r:+m[1], g:+m[2], b:+m[3] } : null;
    };

    const isTransparent = (s) => !s || s === 'rgba(0, 0, 0, 0)' || s === 'transparent';

    const getCls = (el) => {
        if (!el.className) return '';
        return (el.className.baseVal != null) ? el.className.baseVal : (typeof el.className === 'string' ? el.className : '');
    };

    // --- Parse ALL config sections ---
    const brandColors = (config.brandColors || []).map(c => ({...hexToRgb(c.hex||'#000'), label:c.label||'', hex:c.hex||''}));
    const neutralColors = (config.neutralColors || []).map(c => ({...hexToRgb(c.hex||'#000'), label:c.label||'', hex:c.hex||''}));
    const allBrandColors = [...brandColors, ...neutralColors];

    const spacingTokens = parseTokens(config.spacing);
    const imgSizeLimitKB = parseFloat(config.imgSizeLimitKB) || 44;
    const typo = config.typography || {};
    const allowedFontSizes = parseTokens(typo.sizes);
    const fontFamilyRaw = typo.family || '';
    const fontFamilyParts = fontFamilyRaw.toLowerCase().split(',').map(s => s.trim().replace(/['"]/g,''));

    // Button rules (all three types combined)
    const btns = config.buttons || {};
    const primaryH = parseTokens((btns.primary||{}).height);
    const primaryR = parseTokens((btns.primary||{}).radius);
    const secondaryH = parseTokens((btns.secondary||{}).height);
    const secondaryR = parseTokens((btns.secondary||{}).radius);
    const dashedH = parseTokens((btns.dashed||{}).height);
    const allBtnH = [...new Set([...primaryH,...secondaryH,...dashedH])];
    const allBtnR = [...new Set([...primaryR,...secondaryR])];

    // Input rules
    const inps = config.inputs || {};
    const inputH = parseTokens((inps.text||{}).height);
    const inputR = parseTokens((inps.text||{}).radius);

    // Display component rules
    const disp = config.display || {};
    const navH = parseTokens((disp.nav||{}).height);
    const paginationH = parseTokens((disp.pagination||{}).height);
    const tableRowH = parseTokens((disp.table||{}).rowHeight);
    const tagH = parseTokens((disp.tag||{}).height);
    const tagR = parseTokens((disp.tag||{}).radius);

    // Feature flags (default true if not explicitly false)
    const doCheckBtn = config.checkButtonState !== false;
    const doCheckInp = config.checkInputState !== false;
    const doCheckTable = config.checkTableAlignment !== false;
    const doCheckNav = config.checkFormSpacing !== false;

    const seen = new Set();

    const addIssue = (el, title, level, category, desc, suggestion) => {
        try {
            const r = el.getBoundingClientRect();
            if (!r || r.width <= 0 || r.height <= 0) return;
            issues.push({ id: issueId++, title, level, category, desc, suggestion,
                rect: { top: r.top+window.scrollY, left: r.left+window.scrollX, width: r.width, height: r.height } });
        } catch(e) {}
    };

    const checkBgColor = (el, category, name) => {
        if (!allBrandColors.length) return;
        try {
            const bg = window.getComputedStyle(el).backgroundColor;
            if (isTransparent(bg)) return;
            const rgb = parseRgbStr(bg);
            if (!rgb) return;
            if (rgb.r > 245 && rgb.g > 245 && rgb.b > 245) return; // skip near-white
            let nearest = null, nd = 9999;
            allBrandColors.forEach(c => { const d = colorDist(rgb, c); if (d < nd) { nd=d; nearest=c; } });
            if (nearest && nd > 5 && nd < 55) {
                addIssue(el, '品牌色偏离', 'warning', category,
                    `${name}背景色与规范色 ${nearest.label}(${nearest.hex}) 偏差过大(差值:${Math.round(nd)})`,
                    `请校准为规范色: ${nearest.label} ${nearest.hex}`);
            }
        } catch(e) {}
    };

    // --- Element selector covering all component types ---
    const sel = [
        'button','.ant-btn','.el-button',
        'input:not([type=radio]):not([type=checkbox]):not([type=file]):not([type=hidden])',
        'textarea','select','.ant-input','.el-input__inner','.ant-select-selector',
        'nav','header','.navbar','.ant-menu','.el-menu','.ant-layout-sider',
        '.ant-pagination','.el-pagination',
        'table','.ant-table','.el-table__body-wrapper',
        '.ant-tag','.el-tag',
        'h1','h2','h3','h4','p','a'
    ].join(',');

    Array.from(document.querySelectorAll(sel)).forEach(el => {
        if (seen.has(el)) return;
        seen.add(el);
        try {
            const rect = el.getBoundingClientRect();
            if (!rect || rect.width <= 2 || rect.height <= 2) return;
            const h = Math.round(rect.height);
            const tag = el.tagName.toLowerCase();
            const cls = getCls(el);
            const style = window.getComputedStyle(el);

            const isBtn = tag === 'button' || /\\bant-btn\\b|\\bel-button\\b/.test(cls);
            const isInp = (tag === 'input' && !['radio','checkbox','file','hidden'].includes(el.type))
                        || tag === 'textarea' || /ant-input|el-input__inner/.test(cls);
            const isSel = tag === 'select' || /ant-select-selector|el-select/.test(cls);
            const isNav = tag === 'nav' || tag === 'header'
                        || /\\bnavbar\\b|\\bant-menu\\b|\\bel-menu\\b|ant-layout-sider/.test(cls);
            const isPag = /ant-pagination|el-pagination|\\bpagination\\b/.test(cls);
            const isTbl = tag === 'table' || /\\bant-table\\b|el-table__body-wrapper/.test(cls);
            const isTagEl = /\\bant-tag\\b|\\bel-tag\\b/.test(cls);
            const isText = ['h1','h2','h3','h4','p','a'].includes(tag);

            // --- Button checks (all types) ---
            if (doCheckBtn && isBtn) {
                if (allBtnH.length && !matchesToken(h, allBtnH))
                    addIssue(el, '按钮高度异常', 'high', '按钮规范',
                        `按钮实测高度 ${h}px`, `规范高度: ${allBtnH.join(', ')}px`);
                const r = parseFloat(style.borderRadius);
                if (allBtnR.length && !isNaN(r) && r > 0 && !matchesToken(r, allBtnR))
                    addIssue(el, '按钮圆角异常', 'medium', '按钮规范',
                        `按钮实测圆角 ${r}px`, `规范圆角: ${allBtnR.join(', ')}px`);
                checkBgColor(el, '按钮规范', '按钮');
            }

            // --- Input checks ---
            if (doCheckInp && isInp) {
                if (inputH.length && !matchesToken(h, inputH))
                    addIssue(el, '输入框高度异常', 'high', '表单规范',
                        `输入框实测高度 ${h}px`, `规范高度: ${inputH.join(', ')}px`);
                const r = parseFloat(style.borderRadius);
                if (inputR.length && !isNaN(r) && !matchesToken(r, inputR))
                    addIssue(el, '输入框圆角异常', 'medium', '表单规范',
                        `输入框实测圆角 ${r}px`, `规范圆角: ${inputR.join(', ')}px`);
            }

            // --- Select checks (reuse input height rules) ---
            if (doCheckInp && isSel) {
                if (inputH.length && !matchesToken(h, inputH))
                    addIssue(el, '选择器高度异常', 'high', '表单规范',
                        `选择器实测高度 ${h}px`, `规范高度: ${inputH.join(', ')}px`);
            }

            // --- Navbar checks ---
            if (doCheckNav && isNav) {
                if (navH.length && !matchesToken(h, navH))
                    addIssue(el, '导航栏高度异常', 'medium', '导航规范',
                        `导航栏实测高度 ${h}px`, `规范高度: ${navH.join(', ')}px`);
            }

            // --- Pagination checks ---
            if (isPag) {
                if (paginationH.length && !matchesToken(h, paginationH))
                    addIssue(el, '分页高度异常', 'medium', '导航规范',
                        `分页实测高度 ${h}px`, `规范高度: ${paginationH.join(', ')}px`);
            }

            // --- Table row height checks ---
            if (doCheckTable && isTbl) {
                const fr = el.querySelector('tr');
                if (fr) {
                    const rowH2 = Math.round(fr.getBoundingClientRect().height);
                    if (tableRowH.length && !matchesToken(rowH2, tableRowH))
                        addIssue(el, '表格行高异常', 'low', '展示规范',
                            `实测行高 ${rowH2}px`, `规范行高: ${tableRowH.join(', ')}px`);
                }
            }

            // --- Tag (chip) checks ---
            if (isTagEl) {
                if (tagH.length && !matchesToken(h, tagH))
                    addIssue(el, '标签高度异常', 'low', '展示规范',
                        `标签实测高度 ${h}px`, `规范高度: ${tagH.join(', ')}px`);
                const r = parseFloat(style.borderRadius);
                if (tagR.length && !isNaN(r) && !matchesToken(r, tagR))
                    addIssue(el, '标签圆角异常', 'low', '展示规范',
                        `标签实测圆角 ${r}px`, `规范圆角: ${tagR.join(', ')}px`);
            }

            // --- Typography checks ---
            if (isText && el.innerText && el.innerText.trim()) {
                const fs = parseFloat(style.fontSize);
                if (allowedFontSizes.length && !matchesToken(fs, allowedFontSizes))
                    addIssue(el, '字号不规范', 'medium', '排版规范',
                        `实测字号 ${fs}px，不在规范字阶内`, `规范字阶: ${allowedFontSizes.join(', ')}px`);
                if (fontFamilyParts.length && fontFamilyParts[0]) {
                    const ff = style.fontFamily.toLowerCase();
                    if (!fontFamilyParts.some(f => f && ff.includes(f)))
                        addIssue(el, '字体族不匹配', 'medium', '排版规范',
                            `实测字体: ${style.fontFamily}`, `规范字体: ${fontFamilyRaw}`);
                }
            }
        } catch(e) {}
    });

    // --- Form item spacing check（与基准值模式一致：须为间距基准 px 的整数倍，非「仅等于」某一档） ---
    if (spacingTokens.length) {
        try {
            document.querySelectorAll('.ant-form-item,.el-form-item,.form-group,.form-row').forEach(item => {
                const mb = parseFloat(window.getComputedStyle(item).marginBottom);
                if (mb > 5 && !isMultipleOfAnyPx(mb, spacingTokens)) {
                    const r = item.getBoundingClientRect();
                    issues.push({ id: issueId++, title: '表单项间距异常', level: 'medium', category: '间距规范',
                        desc: `表单项下边距 ${mb}px`, suggestion: `下边距须为 ${spacingTokens.join('、')} 中任一 px 值的整数倍`,
                        rect: { top: r.top+window.scrollY, left: r.left+window.scrollX, width: r.width, height: r.height } });
                }
            });
        } catch(e) {}
    }

    
                // ==========================================
                // 性能：图片资源大小检测 (通过 performance API)
                // ==========================================
                const resources = window.performance.getEntriesByType('resource');
                resources.forEach(res => {
                    if ((res.initiatorType === 'img' || res.name.match(/\.(png|jpe?g|webp|gif)/i)) && res.transferSize > 0) {
                        const sizeKB = res.transferSize / 1024;
                        if (sizeKB > imgSizeLimitKB) {
                            issues.push({ id: issueId++, title: "图片体积过大", level: "warning", category: "性能与质量", desc: `图片 ${(res.name||'').split('/').pop().substring(0,20)} 体积 ${sizeKB.toFixed(1)}KB`, suggestion: `限制单张图片最大 ${imgSizeLimitKB}KB`, rect: {top:0,left:0,width:0,height:0} });
                        }
                    }
                });

                return issues;
            }
"""
            issues = await page.evaluate(js_auditor, config)
            await browser.close()
            
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

                // --- 1. 提取基准值配置 ---
                /** 单个 token 转成正数 px（统一去 px、trim，避免数组元素解析丢基准） */
                const coercePxToken = (v) => {
                    if (v == null || v === '') return NaN;
                    const s = String(v).trim().replace(/px$/i, '').trim();
                    const n = parseFloat(s);
                    return (Number.isFinite(n) && n > 0) ? n : NaN;
                };
                const parseNumericTokens = (raw, fallback = []) => {
                    if (Array.isArray(raw)) {
                        const arr = raw.map((v) => coercePxToken(v)).filter((n) => !Number.isNaN(n));
                        return arr.length ? arr : fallback;
                    }
                    if (typeof raw === 'string') {
                        const arr = raw.split(',').map((s) => coercePxToken(s.trim())).filter((n) => !Number.isNaN(n));
                        return arr.length ? arr : fallback;
                    }
                    return fallback;
                };
                /** 间距/栅格/圆角：去重后的正数基准列表 */
                const parsePxTokenList = (raw) => {
                    const arr = parseNumericTokens(raw, []);
                    return [...new Set(arr.map((n) => Math.round(n)))].filter((n) => n > 0);
                };
                const matchesAnyToken = (val, tokens, tolerance = 0.1) =>
                    tokens.some(t => Math.abs(val - t) <= tolerance);

                /** 实测值（px）是否为任一基准值的整数倍；≤0 视为通过 */
                const isMultipleOfAnyPx = (val, bases) => {
                    const vf = Number(val);
                    if (Number.isNaN(vf) || vf <= 0) return true;
                    if (!bases || bases.length === 0) return true;
                    const v = Math.round(vf);
                    return bases.some((g) => {
                        const base = Math.round(Number(g));
                        if (Number.isNaN(base) || base <= 0) return false;
                        return (v % base + base) % base === 0;
                    });
                };

                const allowedFonts = parseNumericTokens(config.fontTokens || config.fontSizes, [12, 14, 16, 32]);
                const allowedLineHeights = parseNumericTokens(config.lineHeights, [1.2, 1.5, 1.6]);
                const minClickArea = config.minClickArea || 44;
                const colorTolerance = config.colorTolerance || 2; // ΔE 容差
                let allowedSpacing = parsePxTokenList(config.spacingTokens);
                if (!allowedSpacing.length) allowedSpacing = [4, 8, 16];
                console.log('[UI-Audit] allowedSpacing resolved to:', JSON.stringify(allowedSpacing), 'from config.spacingTokens:', JSON.stringify(config.spacingTokens));

                let allowedGrids = parsePxTokenList(config.gridTokens);
                if (!allowedGrids.length) allowedGrids = [8];

                let allowedRadius = parsePxTokenList(config.radiusTokens);
                if (!allowedRadius.length) allowedRadius = [4, 8, 12];
                const parseTransitionList = (raw) => {
                    if (typeof raw === 'string' && raw.trim()) {
                        const arr = raw.split(',').map(s => s.trim()).filter(Boolean);
                        if (arr.length) return arr;
                    }
                    return ['0.2s', '0.3s'];
                };
                const allowedTransitions = parseTransitionList(config.transitions);
                const legacyBtnInp = config.buttonInputCheck !== false;
                const buttonHeightCheck = ('buttonHeightCheck' in config) ? (config.buttonHeightCheck !== false) : legacyBtnInp;
                const inputSelectHeightCheck = ('inputSelectHeightCheck' in config) ? (config.inputSelectHeightCheck !== false) : legacyBtnInp;
                const btnHeightList = parseNumericTokens(config.buttonHeightTokens, []);
                const inpHeightList = parseNumericTokens(config.inputHeightTokens, []);
                const imgSizeLimitKB = config.imgSizeLimitKB || 44;
                
                // 预设 Ant Design 阴影规则
                const allowedShadows = [
                    '0px 2px 8px 0px rgba(0, 0, 0, 0.15)', 'none', '0px 0px 0px 0px rgba(0, 0, 0, 0)'
                ];

                const brandColors = (config.colors || [{hex: '#1A6AFF', label: '主题色'}, {hex: '#47B7FF', label: 'hover色'}, {hex: '#145BD7', label: '点击色'}]).map(c => {
                    const hex = (c.hex || '').replace('#', '');
                    return {
                        r: parseInt(hex.substring(0, 2), 16) || 0,
                        g: parseInt(hex.substring(2, 4), 16) || 0,
                        b: parseInt(hex.substring(4, 6), 16) || 0,
                        label: c.label, hex: c.hex
                    };
                });
                
                const colorDistance = (rgb1, rgb2) => Math.sqrt(Math.pow(rgb1.r - rgb2.r, 2) + Math.pow(rgb1.g - rgb2.g, 2) + Math.pow(rgb1.b - rgb2.b, 2));
                const rgbToHex = (r, g, b) => '#' + [r, g, b].map(x => Math.max(0, Math.min(255, x | 0)).toString(16).padStart(2, '0')).join('').toUpperCase();
                const normalizeHex = (h) => {
                    const s = (h || '').replace(/^#/, '');
                    if (s.length === 6) return '#' + s.toUpperCase();
                    return '';
                };
                const getLuminance = (r, g, b) => {
                    const a = [r, g, b].map(v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); });
                    return a[0] * 0.2126 + a[1] * 0.7152 + a[2] * 0.0722;
                };
                const getContrast = (l1, l2) => (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);

                const els = document.querySelectorAll('*');
                let lastHeadingLevel = 0;

                Array.from(els).forEach((el) => {
                    const tag = el.tagName.toLowerCase();
                    if (['script', 'style', 'meta', 'head', 'html', 'body', 'link', 'noscript'].includes(tag)) return;
                    
                    const style = window.getComputedStyle(el);
                    const rect = el.getBoundingClientRect();
                    if (!rect || rect.width <= 0 || rect.height <= 0) return;
                    const cords = { top: rect.top + window.scrollY, left: rect.left + window.scrollX, width: rect.width, height: rect.height };

                    const svgInnerTags = ['svg','path','line','circle','rect','g','polyline','polygon','ellipse','use','defs','clippath','mask','symbol','text','tspan'];
                    const isInteractive = ['button', 'a', 'input', 'select', 'textarea'].includes(tag) ||
                        (style.cursor === 'pointer' && !svgInnerTags.includes(tag) && !el.closest('[aria-hidden="true"]'));
                    const hasText = el.innerText && el.innerText.trim().length > 0;

                    // ==========================================
                    // 1. 视觉一致性标准
                    // ==========================================
                    
                    // 1.1 全局色盘
                    if (brandColors.length > 0) {
                        const bgMatch = style.backgroundColor.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
                        if (bgMatch && style.backgroundColor !== 'rgba(0, 0, 0, 0)' && style.backgroundColor !== 'transparent') {
                            const bgRgb = { r: parseInt(bgMatch[1]), g: parseInt(bgMatch[2]), b: parseInt(bgMatch[3]) };
                            if (!(bgRgb.r > 245 && bgRgb.g > 245 && bgRgb.b > 245)) {
                                let nearestDist = 999;
                                let nearestBc = brandColors[0];
                                brandColors.forEach(bc => {
                                    const dist = colorDistance(bgRgb, bc);
                                    if (dist < nearestDist) { nearestDist = dist; nearestBc = bc; }
                                });
                                const measuredHex = rgbToHex(bgRgb.r, bgRgb.g, bgRgb.b);
                                const targetHex = normalizeHex(nearestBc.hex) || rgbToHex(nearestBc.r, nearestBc.g, nearestBc.b);
                                const targetLabel = nearestBc.label || '规范色';
                                // 模拟 Delta E > 容差
                                if (nearestDist > colorTolerance * 2.5) {
                                    issues.push({ id: issueId++, title: "颜色偏离色盘", level: "warning", category: "视觉", desc: `实测颜色: ${measuredHex}`, suggestion: `请校准为规范色：${targetLabel} ${targetHex}`, rect: cords });
                                }
                            }
                        }
                    }

                    // 1.2 字体与排版
                    if (hasText && ['h1','h2','h3','h4','h5','h6','p','span','a','button','div'].includes(tag)) {
                        const ff = style.fontFamily.toLowerCase();
                        if (!ff.includes('微软雅黑') && !ff.includes('pingfang sc')) {
                            issues.push({ id: issueId++, title: "字体族违规", level: "medium", category: "视觉", desc: `实测 ${style.fontFamily}`, suggestion: `须包含 微软雅黑 或 PingFang SC`, rect: cords });
                        }
                        
                        const fs = parseFloat(style.fontSize);
                        if (!matchesAnyToken(fs, allowedFonts, 0.5)) {
                            issues.push({ id: issueId++, title: "字号不在基准值内", level: "medium", category: "视觉", desc: `实测 ${fs}px`, suggestion: `规范字号为: ${allowedFonts.join(', ')}`, rect: cords });
                        }

                        const lh = parseFloat(style.lineHeight);
                        if (!isNaN(lh) && fs > 0) {
                            const ratio = lh / fs;
                            if (!allowedLineHeights.some(allowed => Math.abs(ratio - allowed) < 0.05)) {
                                issues.push({ id: issueId++, title: "行高异常", level: "medium", category: "视觉", desc: `倍数 ${ratio.toFixed(2)}`, suggestion: `规范行高为: ${allowedLineHeights.join(', ')}`, rect: cords });
                            }
                        }

                        const fw = style.fontWeight;
                        if (!['400', '600', 'normal', 'bold'].includes(fw)) {
                            issues.push({ id: issueId++, title: "字重异常", level: "low", category: "视觉", desc: `实测 ${fw}`, suggestion: `规范为 400 或 600`, rect: cords });
                        }
                    }

                    // 1.3 栅格（仅全局布局尺寸）：只校验布局类容器「宽度」是否对齐栅格基准；margin/padding 属间距规范，见下方「间距不规范」，避免与栅格混用同一套倍数规则
                    const isLayout = el.className && typeof el.className === 'string' && /(row|col|grid|container|wrapper|layout)/i.test(el.className);
                    if (config.gridCheck !== false && isLayout) {
                        const w = Math.round(rect.width);
                        const gridHint = allowedGrids.length ? `${allowedGrids.join('、')} 中任一 px 值的整数倍` : '规范栅格基准';
                        if (w > 0 && !isMultipleOfAnyPx(w, allowedGrids)) {
                            issues.push({ id: issueId++, title: "容器宽度未对齐栅格", level: "low", category: "视觉", desc: `实测宽度 ${w}px`, suggestion: `须为 ${gridHint}`, rect: cords });
                        }
                    }

                    const brStr = style.borderRadius || '';
                    const brStrTrim = String(brStr).trim();
                    const brFirst = /%/.test(brStrTrim) ? NaN : parseFloat(brStrTrim.split(/\\s+/)[0]);
                    if (config.radiusCheck !== false && !isNaN(brFirst) && brFirst > 0 && !isMultipleOfAnyPx(brFirst, allowedRadius)) {
                        const radiusHint = allowedRadius.length ? `${allowedRadius.join('、')} 中任一 px 值的整数倍` : '规范圆角基准';
                        issues.push({ id: issueId++, title: "圆角不规范", level: "medium", category: "视觉", desc: `实测 ${brStr}`, suggestion: `圆角须为 ${radiusHint}`, rect: cords });
                    }
                    // 间距规范：配置项为基准 px，外边距/内边距须为其中任一数的整数倍（满足其一即通过）
                    const spacingHint = allowedSpacing.length ? `${allowedSpacing.join('、')} 中任一 px 值的整数倍` : '规范间距基准';
                    ['marginTop', 'marginBottom', 'marginLeft', 'marginRight', 'paddingTop', 'paddingBottom', 'paddingLeft', 'paddingRight'].forEach(prop => {
                        const val = parseFloat(style[prop]);
                        if (!isNaN(val) && val > 0 && !isMultipleOfAnyPx(val, allowedSpacing)) {
                            issues.push({ id: issueId++, title: "间距不规范", level: "low", category: "视觉", desc: `实测 ${prop}: ${val}px`, suggestion: `外边距/内边距须为 ${spacingHint}`, rect: cords });
                        }
                    });

                    // 1.4 阴影与图标
                    const shadow = style.boxShadow;
                    if (shadow && shadow !== 'none' && !allowedShadows.some(s => shadow.includes(s) || s.includes(shadow))) {
                        if (!shadow.includes('rgba(0, 0, 0, 0.15)')) { // 简易判断 AntD 投影特征
                            issues.push({ id: issueId++, title: "投影不符合规范", level: "medium", category: "视觉", desc: `实测 ${shadow}`, suggestion: `需符合 Ant Design 投影规范`, rect: cords });
                        }
                    }

                    // 1.5 动画与过渡
                    if (config.transitionCheck !== false) {
                        const transDur = style.transitionDuration;
                        if (transDur && transDur !== '0s') {
                            const durs = transDur.split(',').map(s=>s.trim());
                            if (durs.some(d => !allowedTransitions.includes(d))) {
                                issues.push({ id: issueId++, title: "动画过渡异常", level: "low", category: "视觉", desc: `实测 ${transDur}`, suggestion: `规范过渡时间: ${allowedTransitions.join(', ')}`, rect: cords });
                            }
                        }
                    }

                    // 1.6 按钮与输入框（高度须与配置的规范值一致，严格匹配）
                    if (buttonHeightCheck || inputSelectHeightCheck) {
                        const cls = el.className && typeof el.className === 'string' ? el.className : '';
                        const hEl = Math.round(rect.height);
                        const inpType = (el.type || '').toLowerCase();
                        const isBtnEl = tag === 'button' || /\\bant-btn\\b|\\bel-button\\b/.test(cls);
                        const isInpEl = (tag === 'input' && !['radio','checkbox','file','hidden'].includes(inpType))
                            || tag === 'textarea' || /\\bant-input\\b|\\bel-input__inner\\b|\\bant-select-selector\\b/.test(cls);
                        const hintBtn = btnHeightList.length ? `须为: ${btnHeightList.join(', ')}px` : '';
                        const hintInp = inpHeightList.length ? `须为: ${inpHeightList.join(', ')}px` : '';
                        if (buttonHeightCheck && isBtnEl && btnHeightList.length && hEl > 2 && !matchesAnyToken(hEl, btnHeightList, 0.5)) {
                            issues.push({ id: issueId++, title: "按钮高度不符合规范", level: "medium", category: "视觉", desc: `实测高度 ${hEl}px`, suggestion: hintBtn || `请配置按钮高度规范值`, rect: cords });
                        }
                        if (inputSelectHeightCheck && isInpEl && inpHeightList.length && hEl > 2 && !matchesAnyToken(hEl, inpHeightList, 0.5)) {
                            issues.push({ id: issueId++, title: "输入框/选择器高度不符合规范", level: "medium", category: "视觉", desc: `实测高度 ${hEl}px`, suggestion: hintInp || `请配置输入框/选择器高度规范值`, rect: cords });
                        }
                    }

                    // ==========================================
                    // 2. 交互与布局标准
                    // ==========================================
                    
                    // 2.1 交互反馈
                    if (isInteractive) {
                        if (rect.width < minClickArea || rect.height < minClickArea) {
                            issues.push({ id: issueId++, title: "点击热区过小", level: "high", category: "交互", desc: `实测 ${Math.round(rect.width)}x${Math.round(rect.height)}px`, suggestion: `尺寸应 >= ${minClickArea}px`, rect: cords });
                        }
                        if (el.disabled || el.classList.contains('disabled')) {
                            if (style.cursor !== 'not-allowed') {
                                issues.push({ id: issueId++, title: "禁用状态光标错误", level: "medium", category: "交互", desc: `实测 ${style.cursor}`, suggestion: `应使用 not-allowed`, rect: cords });
                            }
                        } else if (style.cursor !== 'pointer' && tag !== 'input' && tag !== 'textarea') {
                            issues.push({ id: issueId++, title: "可点击元素光标错误", level: "medium", category: "交互", desc: `实测 ${style.cursor}`, suggestion: `应使用 pointer`, rect: cords });
                        }
                    }

                    // 2.2 布局控制
                    if (hasText && style.display === 'block' && (style.width !== 'auto' || style.maxWidth !== 'none')) {
                        if (style.textOverflow !== 'ellipsis' && el.scrollWidth > el.clientWidth) {
                            issues.push({ id: issueId++, title: "文本未作省略处理", level: "medium", category: "布局", desc: `文本溢出容器未加 ellipsis`, suggestion: `默认应使用省略号截断`, rect: cords });
                        }
                    }
                    const zi = parseInt(style.zIndex);
                    if (!isNaN(zi) && zi > 0 && zi < 1000) {
                        if (el.classList.contains('modal') || el.classList.contains('dropdown') || style.position === 'absolute') {
                            if (zi < 100) {
                                issues.push({ id: issueId++, title: "层级过低", level: "warning", category: "布局", desc: `弹窗/下拉菜单 z-index 为 ${zi}`, suggestion: `应置于最高层级防遮挡`, rect: cords });
                            }
                        }
                    }

                    // ==========================================
                    // 3. 无障碍与合规性
                    // ==========================================
                    
                    // 3.1 色彩对比度
                    if (hasText) {
                        const bgMatch = style.backgroundColor.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
                        const fgMatch = style.color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
                        if (bgMatch && fgMatch && style.backgroundColor !== 'rgba(0, 0, 0, 0)') {
                            const bgLum = getLuminance(parseInt(bgMatch[1]), parseInt(bgMatch[2]), parseInt(bgMatch[3]));
                            const fgLum = getLuminance(parseInt(fgMatch[1]), parseInt(fgMatch[2]), parseInt(fgMatch[3]));
                            const ratio = getContrast(bgLum, fgLum);
                            if (ratio < 4.5) {
                                issues.push({ id: issueId++, title: "对比度不足", level: "high", category: "无障碍", desc: `实测 ${ratio.toFixed(2)}:1`, suggestion: `AA级标准要求 >= 4.5:1`, rect: cords });
                            }
                        }
                    }

                    // 3.2 图片 Alt
                    if (tag === 'img') {
                        if (!el.hasAttribute('alt') || el.getAttribute('alt').trim() === '') {
                            issues.push({ id: issueId++, title: "缺失 Alt 属性", level: "high", category: "无障碍", desc: `<img> 标签未配置 alt`, suggestion: `强制要求添加替代文本`, rect: cords });
                        }
                    }

                    // 3.3 DOM 语义化
                    const headingMatch = tag.match(/^h([1-6])$/);
                    if (headingMatch) {
                        const level = parseInt(headingMatch[1]);
                        if (lastHeadingLevel > 0 && level - lastHeadingLevel > 1) {
                            issues.push({ id: issueId++, title: "标题层级跨级", level: "medium", category: "无障碍", desc: `从 H${lastHeadingLevel} 跳到 H${level}`, suggestion: `层级顺序不可跨级`, rect: cords });
                        }
                        lastHeadingLevel = level;
                    }
                    
                    // ==========================================
                    // 4. 性能与内容质量
                    // ==========================================
                    
                    // 4.1 死链扫描
                    if (tag === 'a' && el.href) {
                        if (el.href.startsWith('http') && el.href.includes('404')) {
                            issues.push({ id: issueId++, title: "发现疑似死链", level: "high", category: "质量", desc: `链接包含 404: ${el.href}`, suggestion: `请确保链接可用`, rect: cords });
                        }
                    }

                    // 4.2 中英文空格
                    if (hasText) {
                        const walk = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null, false);
                        let node;
                        while(node = walk.nextNode()) {
                            const txt = node.textContent;
                            if (/[a-zA-Z][\u4e00-\u9fa5]|[\u4e00-\u9fa5][a-zA-Z]/.test(txt)) {
                                issues.push({ id: issueId++, title: "中英文未加空格", level: "low", category: "质量", desc: `检测到中英文混合无空格`, suggestion: `中英文之间必须加空格`, rect: cords });
                                break;
                            }
                        }
                    }

                    // 4.3 日期格式
                    if (hasText) {
                        const txt = el.innerText;
                        if (/\d{4}[/\.]\d{1,2}[/\.]\d{1,2}/.test(txt)) {
                            issues.push({ id: issueId++, title: "日期格式不规范", level: "medium", category: "质量", desc: `检测到非标日期: ${txt.substring(0,15)}`, suggestion: `全局统一为 YYYY-MM-DD`, rect: cords });
                        }
                    }
                });

                
                // ==========================================
                // 性能：图片资源大小检测 (通过 performance API)
                // ==========================================
                const resources = window.performance.getEntriesByType('resource');
                resources.forEach(res => {
                    if ((res.initiatorType === 'img' || res.name.match(/\.(png|jpe?g|webp|gif)/i)) && res.transferSize > 0) {
                        const sizeKB = res.transferSize / 1024;
                        if (sizeKB > imgSizeLimitKB) {
                            issues.push({ id: issueId++, title: "图片体积过大", level: "warning", category: "性能与质量", desc: `图片 ${(res.name||'').split('/').pop().substring(0,20)} 体积 ${sizeKB.toFixed(1)}KB`, suggestion: `限制单张图片最大 ${imgSizeLimitKB}KB`, rect: {top:0,left:0,width:0,height:0} });
                        }
                    }
                });

                return issues;
            }
"""
            _normalize_baseline_config_keys(config)
            print(f"[UI-Audit] baseline config spacingTokens = {config.get('spacingTokens')}")
            print(f"[UI-Audit] baseline config gridTokens    = {config.get('gridTokens')}")
            issues = await page.evaluate(js_auditor, config)
            await browser.close()

        # 生成 AI 诊断总结
        diagnosis = await generate_diagnosis(issues)
        
        # 🌟 优化后的加权算分逻辑
        high_count = len([i for i in issues if i.get('level') == 'high'])
        medium_count = len([i for i in issues if i.get('level') == 'medium'])
        low_count = len([i for i in issues if i.get('level') == 'low' or i.get('level') == 'warning'])
        issue_count = len(issues)
        
        # 设计还原度评分 (Restoration Score)
        # 高优扣8分，中优扣3分，低优扣1分
        score = max(0, 100 - (high_count * 8 + medium_count * 3 + low_count * 1))
        
        # 设计规范符合度 (Compliance Score)
        # 规范合规对严重违规更敏感：高优扣10分，中优扣4分，低优扣1分
        compliance = max(0, 100 - (high_count * 10 + medium_count * 4 + low_count * 1))

        return {
            "score": score,
            "compliance": compliance,
            "issueCount": issue_count,
            "issues": issues,
            "diagnosis": diagnosis,
            "screenshot": screenshot_base64,
            "url": url,
            "mode": mode # 记录当前使用的模式
        }