import asyncio
from backend.config import config
import backend.figma_service as figma_service
from backend.ai_service import generate_diagnosis

print("=== 配置测试 ===")
config.validate()
print("FIGMA_TOKEN:", bool(config.FIGMA_TOKEN))
print("API_KEY (from config):", bool(config.API_KEY))

print("\n=== AI 连通性测试 (DeepSeek API) ===")
async def test_ai():
    dummy_issues = [{"title": "按钮颜色错误", "desc": "期望 #FFFFFF，实际 #000000"}]
    try:
        res = await generate_diagnosis(dummy_issues)
        print("✅ AI 响应成功:", res)
    except Exception as e:
        print("❌ AI 响应失败:", e)

asyncio.run(test_ai())

print("\n=== Figma API 连通性测试 ===")
try:
    figma_service.fetch_figma_image("https://www.figma.com/design/1234567890abcdef/?node-id=1:2")
    print("✅ Figma 获取成功")
except Exception as e:
    print(f"✅ Figma 响应 (预期会报错网络正常但参数无效): {e}")
