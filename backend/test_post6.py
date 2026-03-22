import asyncio
import httpx
import json
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

def run_server():
    server = HTTPServer(('localhost', 8004), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

async def main():
    config = {
        "spacingTokens": ["10px", "20px"],
        "fontSizes": "32, 16, 14, 12, 44",
        "fontFamily": "微软雅黑, PingFang SC",
        "gridTokens": ["8px"],
        "radiusTokens": ["4px", "8px", "12px"],
        "colors": [{"hex": "#1A6AFF", "label": "主题色"}],
        "buttonHeightCheck": False,
        "inputSelectHeightCheck": False,
        "lineHeights": "1.2, 1.4, 1.5, 1.6",
        "colorTolerance": "< 2ΔE",
        "shadowCheck": False,
        "contrastCheck": False,
        "altCheck": False,
        "textFormatCheck": False,
        "deadlinkCheck": False
    }
    
    html_content = '<html><body style="margin: 0;"><div style="box-shadow: 1px 1px 1px red; font-size: 44px; line-height: 1.5; font-family: 微软雅黑, sans-serif; margin-bottom: 20px;">Hello World 123<img src="foo.jpg"><a href="http://foo.bar/404">link</a></div></body></html>'
    with open("test6.html", "w") as f:
        f.write(html_content)
        
    url = f"http://localhost:8004/test6.html"
    
    async with httpx.AsyncClient(timeout=None) as client:
        res = await client.post('http://localhost:8000/api/audit', json={
            "url": url,
            "mode": "baseline",
            "config": config,
            "user_id": 1
        })
        print(res.status_code)
        data = res.json()
        print("Issues found:")
        for issue in data["data"]["issues"]:
            print(issue["title"], "->", issue["desc"])

asyncio.run(main())
