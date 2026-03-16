import asyncio
import os

from core_auditor import run_audit_task

async def test_baseline_audit():
    print("\n=== 核心算法测试: 基准值走查模式 (DOM AST) ===")
    config = {
        "fontTokens": [12, 14, 16, 18, 20, 24, 32],
        "altCheck": True,
        "webpCheck": True,
        "nearColorCheck": False
    }
    url = "https://example.com"
    print(f"📡 正在爬取和分析页面: {url}")
    try:
        res = await run_audit_task(url, config, mode="baseline")
        print("✅ DOM 走查执行成功！")
        print(f"📊 得分: {res['score']}, 违规项数量: {res['issueCount']}")
        print(f"🤖 AI 诊断总结: {res['diagnosis']}")
        if res['issueCount'] > 0:
            print("🔍 部分发现的问题:")
            for issue in res['issues'][:3]:
                print(f"  - [{issue['category']}] {issue['title']}: {issue['desc']}")
    except Exception as e:
        print("❌ DOM 走查执行失败:", e)

if __name__ == "__main__":
    asyncio.run(test_baseline_audit())
