import requests
import re
from .config import config
# 🚨🚨🚨 在这里填入您刚刚申请的 Figma Personal Access Token 🚨🚨🚨
FIGMA_TOKEN = config.FIGMA_TOKEN

def fetch_figma_image(url: str):
    """解析 Figma 链接，调用 API 下载对应的 Node 节点截图"""
    print(f"🔗 正在解析 Figma 资源: {url}")
    
    # 提取 File Key 和 Node ID
    # 支持的新版 /design/ 链接和旧版 /file/ 链接
    file_key_match = re.search(r'figma\.com/(?:file|design)/([a-zA-Z0-9]+)', url)
    node_id_match = re.search(r'node-id=([^&]+)', url)

    if not file_key_match or not node_id_match:
        raise ValueError("无效的 Figma 链接，请确保您复制的是某个具体画板/元素的链接（必须包含 node-id）")
    
    file_key = file_key_match.group(1)
    # Figma URL 里经常用 '-' 代替 ':'，这里做兼容替换
    node_id = node_id_match.group(1).replace('-', ':') 

    headers = {"X-Figma-Token": FIGMA_TOKEN}
    # scale=1 保证 1:1 像素导出，不进行 2x 放大
    api_url = f"https://api.figma.com/v1/images/{file_key}?ids={node_id}&scale=1&format=png"
    
    print("☁️ 正在向 Figma 服务器请求图层数据...")
    resp = requests.get(api_url, headers=headers)
    
    if resp.status_code != 200:
        raise Exception(f"Figma API 拒绝访问，请检查 Token 权限或网络。({resp.status_code})")
    
    data = resp.json()
    images = data.get("images", {})
    
    # 获取真实的 CDN 图片下载链接
    img_url = images.get(node_id) or images.get(node_id.replace(':', '-'))
    
    if not img_url:
        raise Exception("Figma 提取图片失败，可能是该节点已被删除或无访问权限。")

    print("⬇️ 正在下载 Figma 原画级资源...")
    img_resp = requests.get(img_url)
    
    return img_resp.content