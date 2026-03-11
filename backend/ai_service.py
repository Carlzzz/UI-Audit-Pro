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

    请根据这些问题，写一段简短、专业的【整体诊断与修复建议】（100字左右）。
    要求语气专业，指出问题的核心危害，并给出高层次的修改方向。不要使用 Markdown 列表格式，直接输出纯文本段落即可。
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