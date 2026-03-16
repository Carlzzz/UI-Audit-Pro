import os
import shutil
from datetime import datetime
from playwright.async_api import async_playwright

async def generate_html_screenshot(html_path: str):
    """
    使用 Playwright 将本地 HTML 文件转换为图片，用于预览和比对
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 统一使用 1440 宽度
        context = await browser.new_context(viewport={'width': 1440, 'height': 1080})
        page = await context.new_page()
        
        # 加载本地文件
        absolute_path = f"file://{os.path.abspath(html_path)}"
        await page.goto(absolute_path, wait_until="networkidle")
        
        # 截取全屏
        png_path = html_path + ".png"
        await page.screenshot(path=png_path, full_page=True)
        await browser.close()
        return png_path
