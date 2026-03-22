"""
设计还原度评分：按四维度权重与检查项总数扣分。
单维度扣分 = 维度权重 × 该维度问题数 ÷ 检查项总数
总还原度 = max(0, 100 − Σ 各维度扣分)
"""

import math
from typing import Any, Dict, List

# 与 frontend/src/utils/issueUrgency.js categoryMapping 对齐
_DIM_WEIGHTS = {
    "functional": 35,
    "interaction": 30,
    "visual": 20,
    "content": 15,
}


def issue_dimension(issue: Dict[str, Any]) -> str:
    title = str(issue.get("title") or "")
    if "图片体积过大" in title:
        return "functional"
    cat = str(issue.get("category") or "")
    functional_kw = ["布局", "系统报错", "功能障碍", "响应式", "死链", "空状态", "加载状态"]
    interaction_kw = ["交互", "无障碍"]
    content_kw = ["质量", "文案", "话术"]
    visual_kw = [
        "视觉",
        "排版规范",
        "按钮规范",
        "表单规范",
        "导航规范",
        "展示规范",
        "间距规范",
        "像素级对比",
    ]
    for kw in functional_kw:
        if kw in cat:
            return "functional"
    for kw in interaction_kw:
        if kw in cat:
            return "interaction"
    for kw in content_kw:
        if kw in cat:
            return "content"
    for kw in visual_kw:
        if kw in cat:
            return "visual"
    return "visual"


def compute_restoration_score(issues: List[Dict[str, Any]], check_item_total: int) -> Dict[str, Any]:
    t = max(1, int(check_item_total) if check_item_total else 1)
    counts = {k: 0 for k in _DIM_WEIGHTS}
    for i in issues:
        counts[issue_dimension(i)] += 1

    deductions = {k: _DIM_WEIGHTS[k] * counts[k] / t for k in _DIM_WEIGHTS}
    total_ded = sum(deductions.values())
    score = max(0, round(100 - total_ded))
    # 单项维度分：100 − 该维扣分，向下取整避免 99.65 被 round 成 100
    dim_scores = {
        k: max(0, int(math.floor(100 - _DIM_WEIGHTS[k] * counts[k] / t + 1e-9)))
        for k in _DIM_WEIGHTS
    }

    return {
        "score": score,
        "checkItemTotal": t,
        "dimensionCounts": counts,
        "dimensionScores": dim_scores,
        "dimensionDeductions": {k: round(deductions[k] * 1000) / 1000 for k in deductions},
    }
