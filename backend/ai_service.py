from openai import OpenAI
import json

# ==========================================
# ⚠️ 填入您真实的 API 密钥！
# ==========================================
API_KEY = "sk-376edfd81a9b41a3af7895fce77383d4" 
BASE_URL = "https://api.deepseek.com" 

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

async def generate_diagnosis(issues: list):
    """双引擎架构：AI 仅负责对确诊结果进行高层级的语义诊断"""
    if not issues:
        return "完美！当前页面完全符合 UI 设计基准规范，未发现任何样式异常。"

    # 将问题列表精简后发给大模型
    summary_data = [{"title": i["title"], "desc": i["desc"]} for i in issues[:10]]
    
    prompt = f"""
    你是一位资深的 UI/UX 设计总监。
    底层自动化爬虫刚刚对网页进行了扫描，发现了以下违背设计规范的问题：
    {json.dumps(summary_data, ensure_ascii=False)}

    请根据这些问题，写【整体诊断与修复建议】（总字数约 150～280 字）。
    格式要求（必须遵守）：
    1. 使用 3～6 条要点，每条单独一行。
    2. 每条行首使用「• 」（圆点 + 空格）。
    3. 需要强调的术语、问题类型、核心危害或修改方向，用半角星号包裹为 **关键词**（Markdown 加粗语法），每条至少包含一处 **...**。
    4. 不要使用 # 标题、不要使用数字编号列表；除上述 ** 外不要用其他 Markdown。
    """
    
    try:
        print("🤖 正在生成高层级 AI 诊断报告...")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ AI 总结生成失败: {str(e)}")
        return "AI 总结生成失败，但这不影响下方具体的样式问题列表，请结合列表数据进行人工复核与修复。"