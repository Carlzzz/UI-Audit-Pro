/**
 * 设计还原度评分（与 backend/restoration_scoring.py 一致）
 * 单维度扣分 = 维度权重 × 该维度问题数 ÷ 检查项总数
 * 总还原度 = max(0, 100 − Σ 各维度扣分)
 */

import { getCategoryType } from './issueUrgency'

export const RESTORATION_WEIGHTS = {
  functional: 35,
  interaction: 30,
  visual: 20,
  content: 15
}

/**
 * @param {Array<{ category?: string, title?: string }>} issues
 * @param {number|undefined} checkItemTotal 检查项总数（来自报告）；缺省时用启发值
 */
export function computeRestorationScore(issues, checkItemTotal) {
  const list = issues || []
  let T = Math.floor(Number(checkItemTotal))
  if (!Number.isFinite(T) || T < 1) {
    T = Math.max(100, list.length * 10)
  }
  const counts = { functional: 0, interaction: 0, visual: 0, content: 0 }
  for (const i of list) {
    const d = getCategoryType(i?.category, i)
    counts[d] += 1
  }
  const deductions = {}
  let sumDed = 0
  for (const k of Object.keys(RESTORATION_WEIGHTS)) {
    const ded = (RESTORATION_WEIGHTS[k] * counts[k]) / T
    deductions[k] = ded
    sumDed += ded
  }
  const score = Math.max(0, Math.round(100 - sumDed))
  const dimensionScores = {}
  for (const k of Object.keys(RESTORATION_WEIGHTS)) {
    dimensionScores[k] = Math.max(
      0,
      Math.floor(100 - (RESTORATION_WEIGHTS[k] * counts[k]) / T + 1e-9)
    )
  }
  return {
    score,
    checkItemTotal: T,
    dimensionCounts: counts,
    dimensionScores,
    dimensionDeductions: deductions
  }
}
