import os
import re

def run_static_scan(file_path: str, config: dict):
    """
    对源文件进行深入静态扫描
    """
    if not os.path.exists(file_path):
        return []

    ext = os.path.splitext(file_path)[1].lower()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='gbk', errors='ignore') as f:
            content = f.read()

    issues = []
    lines = content.split('\n')
    
    # 1. 硬编码中文检测 (增强版)
    if config.get('hardcodeCheck', True):
        for i, line in enumerate(lines):
            clean_line = line.strip()
            if not clean_line or clean_line.startswith('//') or clean_line.startswith('*') or clean_line.startswith('/*'):
                continue
            line_no_comment = re.sub(r'//.*$|/\*.*\*/', '', line)
            line_no_i18n = re.sub(r'\$t\(.*?\)|i18n\.t\(.*?\)|t\(.*?\)', '', line_no_comment)
            chinese_pattern = r'[\u4e00-\u9fa5\u3400-\u4dbf\uf900-\ufaff]'
            if re.search(chinese_pattern, line_no_i18n):
                found_chinese = "".join(re.findall(r'[\u4e00-\u9fa5]+', line_no_i18n))
                if found_chinese:
                    issues.append({
                        "id": f"static-hc-{i}",
                        "title": "源码硬编码中文",
                        "level": "warning",
                        "category": "质量",
                        "desc": f"第 {i+1} 行检测到硬编码文本: \"{found_chinese[:15]}...\"",
                        "suggestion": "请将中文字符串抽取到 i18n 国际化配置文件中",
                        "rect": {"top": 0, "left": 0, "width": 0, "height": 0}
                    })

    # 2. 兜底状态检测 (增强版启发式)
    if ext == '.vue':
        has_loading_state = re.search(r'loading|fetching|processing|pending', content, re.I)
        ui_loading = re.search(r'v-loading|skeleton|spin|loading-bar|<a-spin|<el-loading', content, re.I)
        ui_empty = re.search(r'empty|no-data|v-if=.*!|v-if=.*length === 0|<a-empty|<el-empty|<Empty', content, re.I)

        if len(content) > 1000: 
            if config.get('loadingStateCheck', True) and not (has_loading_state and ui_loading):
                issues.append({
                    "id": "static-missing-loading",
                    "title": "缺失加载状态兜底",
                    "level": "medium",
                    "category": "交互",
                    "desc": "该 Vue 组件源码中未发现 Loading、Skeleton 或异步状态处理逻辑",
                    "suggestion": "为保证用户体验，建议为异步数据加载过程添加骨架屏或加载动画",
                    "rect": {"top": 0, "left": 0, "width": 0, "height": 0}
                })
            
            if config.get('emptyStateCheck', True) and not ui_empty:
                issues.append({
                    "id": "static-missing-empty",
                    "title": "缺失空状态兜底",
                    "level": "medium",
                    "category": "交互",
                    "desc": "组件模板中未发现 Empty、无数据占位图或相应的判断分支",
                    "suggestion": "建议添加空状态占位，避免数据返回为空时页面出现大面积留白",
                    "rect": {"top": 0, "left": 0, "width": 0, "height": 0}
                })

    # 3. HTML 缺失 Alt 检测 (同前)
    if config.get('altCheck', True) and ext in ['.html', '.vue']:
        # 这里的正则可以更健壮一点
        img_tags = re.findall(r'<img\s+[^>]*>', content, re.I)
        for i, tag in enumerate(img_tags):
            # 如果完全没有 alt，或者 alt 是空的 (且没写装饰性 aria-hidden)
            if 'alt=' not in tag.lower() or re.search(r'alt=["\']\s*["\']', tag):
                if 'role="presentation"' not in tag and 'aria-hidden="true"' not in tag:
                    issues.append({
                        "id": f"static-alt-{i}",
                        "title": "静态资源缺失 Alt",
                        "level": "high",
                        "category": "无障碍",
                        "desc": f"源码中存在未定义 alt 属性的 <img> 标签: {tag[:40]}...",
                        "suggestion": "请为图片添加 alt 属性，非装饰性图片需描述内容，装饰性图片可设为空",
                        "rect": {"top": 0, "left": 0, "width": 0, "height": 0}
                    })

    return issues
