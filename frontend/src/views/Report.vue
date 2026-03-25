<template>
  <div v-if="!reportData" class="rpt-missing">
    <AppNavbar variant="report" class="no-print" />
    <div class="rpt-missing-inner">
      <p class="rpt-missing-title">暂无报告数据</p>
      <p class="rpt-missing-desc">刷新后需从本会话快照恢复；若仍无内容，请先完成一次走查或从「历史」打开记录。</p>
      <button type="button" class="btn btn-primary" @click="goTo('/audit-setup')">去新建走查</button>
      <button type="button" class="btn btn-ghost" @click="goTo('/history')">查看历史</button>
    </div>
  </div>
  <div v-else class="rpt-body">
    <AppNavbar variant="report" class="no-print" />

    <div class="rpt-page">
      <div class="rpt-inner">
        <div class="rpt-breadcrumb no-print">
          <a href="#" @click.prevent="goTo('/')">首页</a>
          <span class="sep">></span>
          <span>自动化走查</span>
          <span class="sep">></span>
          <span class="cur">报告详情</span>
        </div>

        <div class="rpt-page-stack">
          <div class="rpt-head-row no-print">
            <h1 class="rpt-head-title">报告详情</h1>
            <div class="rpt-head-actions">
              <button class="btn btn-ghost" @click="goTo('/dashboard')">查看可视化看板</button>
              <button class="btn btn-primary" @click="openExportModal">导出报告</button>
            </div>
          </div>
          <div class="rpt-top-row">
            <div id="left-col" class="rpt-left-stack">
            <div class="rpt-card score-card score-tip-anchor">
              <div class="score-card-hdg">
                页面规范性评分（{{ currentModeName }}）
                <span
                  class="score-tip-icon"
                  @mouseenter="enterMainTip($event)"
                  @mouseleave="leaveMainTip"
                >?</span>
              </div>
              <Transition name="tip-fade">
                <div
                  v-show="showMainTip"
                  ref="mainTipPopupRef"
                  class="score-tip-popup score-tip-popup--fixed"
                  :style="mainTipStyle"
                  @mouseenter="onMainTipPopupEnter"
                  @mouseleave="leaveMainTip"
                >
                  <div class="score-tip-title">评分计算公式</div>
                  <div class="score-tip-formula">还原度 = max(0, 100 − Σ 各维度扣分)；单维度扣分 = 权重 × 该维问题数 ÷ 检查项总数 T（T = {{ restorationDisplay.checkItemTotal }}）</div>
                  <div class="score-tip-detail">
                    <span>功能障碍 35×{{ restorationDisplay.dimensionCounts.functional }}÷T = {{ formatDed(restorationDisplay.dimensionDeductions.functional) }}</span>
                    <span>交互体验 30×{{ restorationDisplay.dimensionCounts.interaction }}÷T = {{ formatDed(restorationDisplay.dimensionDeductions.interaction) }}</span>
                    <span>视觉一致性 20×{{ restorationDisplay.dimensionCounts.visual }}÷T = {{ formatDed(restorationDisplay.dimensionDeductions.visual) }}</span>
                    <span>文案与话术 15×{{ restorationDisplay.dimensionCounts.content }}÷T = {{ formatDed(restorationDisplay.dimensionDeductions.content) }}</span>
                    <span>合计扣分 {{ formatDed(restorationTotalDeduction) }} → 总还原度 {{ displayScore }} 分</span>
                  </div>
                </div>
              </Transition>
              <Transition name="tip-fade">
                <div
                  v-if="activeDimTip"
                  ref="dimTipPopupRef"
                  class="score-tip-popup score-tip-popup--fixed"
                  :style="dimTipStyle"
                  @mouseenter="onDimTipPopupEnter"
                  @mouseleave="leaveDimTip"
                >
                  <div class="score-tip-title">{{ dimTipLabel }} — 维度说明</div>
                  <div class="score-tip-formula">该维度单项分 = max(0, 100 − 权重×问题数÷T)；本维度权重 {{ activeDimWeight }}</div>
                  <div class="score-tip-detail">
                    <span>本维问题数 {{ activeDimCount }}，T = {{ restorationDisplay.checkItemTotal }}</span>
                    <span>本维扣分 = {{ activeDimWeight }} × {{ activeDimCount }} ÷ {{ restorationDisplay.checkItemTotal }} = {{ formatDed(activeDimDeduction) }}</span>
                    <span>本维单项分 {{ dimensionScores[activeDimTip] }} 分</span>
                  </div>
                </div>
              </Transition>
              <div class="score-body">
                <div class="ring-wrap">
                  <svg class="ring-svg" width="110" height="110" viewBox="0 0 110 110">
                    <circle class="ring-bg" cx="55" cy="55" r="44" />
                    <circle class="ring-fg" cx="55" cy="55" r="44"
                      :stroke-dashoffset="ringDashOffset"
                      stroke-dasharray="276.5" />
                  </svg>
                  <div class="ring-label">
                    <div class="ring-score-line">
                      <span class="ring-pct">{{ displayScore || 0 }}</span><span class="ring-unit">分</span>
                    </div>
                    <span class="ring-sub">总评分</span>
                  </div>
                </div>
                <div class="score-detail">
                  <div class="score-badge" :class="scoreBadgeClass">{{ scoreBadgeText }}</div>
                  <div class="score-desc">本次走查发现 {{ reportData.issueCount || 0 }} 个规范问题。建议优先修复高优问题。</div>
                  <div class="score-stats">
                    <div class="stat-block">
                      <div class="stat-val">{{ dimensionScores.functional }}<span class="stat-unit">分</span></div>
                      <div class="stat-label">功能障碍 <span class="score-tip-icon sm" @mouseenter="enterDimTip('functional', $event)" @mouseleave="leaveDimTip">?</span></div>
                    </div>
                    <div class="stat-block">
                      <div class="stat-val">{{ dimensionScores.interaction }}<span class="stat-unit">分</span></div>
                      <div class="stat-label">交互体验 <span class="score-tip-icon sm" @mouseenter="enterDimTip('interaction', $event)" @mouseleave="leaveDimTip">?</span></div>
                    </div>
                    <div class="stat-block">
                      <div class="stat-val">{{ dimensionScores.visual }}<span class="stat-unit">分</span></div>
                      <div class="stat-label">视觉一致性 <span class="score-tip-icon sm" @mouseenter="enterDimTip('visual', $event)" @mouseleave="leaveDimTip">?</span></div>
                    </div>
                    <div class="stat-block">
                      <div class="stat-val">{{ dimensionScores.content }}<span class="stat-unit">分</span></div>
                      <div class="stat-label">文案与话术 <span class="score-tip-icon sm" @mouseenter="enterDimTip('content', $event)" @mouseleave="leaveDimTip">?</span></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="rpt-card distribution-card">
              <div class="distribution-hd">关键问题分布</div>
              <div class="distribution-body">
                <div class="distribution-chart">
                  <div class="chart-item" v-for="(item, idx) in topIssueCategories" :key="idx">
                    <div class="chart-info">
                      <span class="chart-label">{{ item.name }}</span>
                      <span class="chart-count">{{ item.count }} 个问题 ({{ item.percentage }}%)</span>
                    </div>
                    <div class="chart-bar-wrap">
                      <div class="chart-bar" :style="{ width: item.percentage + '%', background: item.color }"></div>
                    </div>
                  </div>
                </div>
                <div class="distribution-summary">
                  <div class="summary-label">AI 问题总结</div>
                  <ul v-if="diagnosisBulletHtmlList.length > 0" class="summary-bullets">
                    <li v-for="(html, idx) in diagnosisBulletHtmlList" :key="idx" v-html="html"></li>
                  </ul>
                  <div v-else class="summary-text" v-html="diagnosisFallbackHtml"></div>
                </div>
              </div>
            </div>
            </div>

            <div class="rpt-sidebar">
            <div class="meta-card meta-card--metadata" role="region" aria-label="报告元数据">
              <div class="meta-card-hd">报告元数据</div>
              <div class="meta-card-body">
                <div class="meta-row">
                  <span class="meta-lbl">目标页面</span>
                  <span class="meta-val">
                    <a
                      v-if="reportData.url"
                      class="meta-link"
                      :href="formattedUrl"
                      target="_blank"
                      rel="noopener noreferrer"
                    >点击访问</a>
                    <span v-else>—</span>
                  </span>
                </div>
                <div class="meta-row">
                  <span class="meta-lbl">操作人员</span>
                  <span class="meta-val">{{ userStore.userInfo ? userStore.userInfo.username : 'Agent' }}</span>
                </div>
                <div class="meta-row">
                  <span class="meta-lbl">走查模式</span>
                  <span class="meta-val">{{ currentModeName }}</span>
                </div>
              </div>
            </div>

            <div class="meta-card snapshot-card" role="region" aria-label="实际页面快照">
              <div class="meta-card-hd">实际页面快照</div>
              <div class="meta-snapshot-block">
                <img
                  v-if="reportData.screenshot"
                  :src="screenshotSrc"
                  class="snapshot-img"
                  alt=""
                  @click="goTo('/dashboard?entry=snapshot')"
                />
                <div v-else class="snapshot-placeholder">此条走查记录暂无快照数据</div>
              </div>
            </div>

            <div class="help-card no-print">
              <div class="help-title">需要帮助？</div>
              <div class="help-desc">如需更多帮助请点击此处</div>
              <div class="help-btn-wrap">
                <button type="button" class="help-btn">反馈问题</button>
                <div class="help-tooltip">此功能开发中，敬请期待</div>
              </div>
            </div>

            <div class="trend-card no-print">
              <div class="trend-head">
                <div class="trend-title">页面规范性趋势分析</div>
                <div class="trend-filter-wrap">
                  <FilterSelect v-model="trendRange" :options="trendRangeOptions" menu-label="趋势时间范围" />
                </div>
              </div>
              <div class="trend-chart" v-if="trendData.length > 0">
                <div class="bar-wrap" v-for="(item, idx) in trendData" :key="item.rowKey">
                  <div class="bar-column" tabindex="0">
                    <div class="trend-tooltip" role="tooltip">
                      <div class="trend-tooltip-row">
                        <span class="trend-tooltip-num">{{ item.score }}</span><span class="trend-tooltip-unit">分</span>
                      </div>
                      <div class="trend-tooltip-date">{{ item.tooltipDate }}</div>
                    </div>
                    <div class="bar-fill" :class="{ today: idx === trendData.length - 1 }" :style="'height:' + Math.max(item.score * 0.6, 10) + 'px'"></div>
                  </div>
                </div>
              </div>
              <div v-else class="trend-empty">暂无足够历史数据</div>
            </div>
          </div>
        </div>
        </div>

        <div class="rpt-issues-section">
          <div class="issue-list-hd">
            <div class="issue-list-title">关键问题清单 <span class="issue-list-cnt">{{ filteredIssues.length }}</span></div>
          </div>
          <div class="issue-tabs-row no-print">
            <div class="issue-tabs-main">
              <button class="tab-btn" :class="{ active: activeTab === 'all' }" @click="activeTab = 'all'">
                全部问题 <span class="tab-badge">{{ allIssues.length }}</span>
              </button>
              <button class="tab-btn" :class="{ active: activeTab === 'functional' }" @click="activeTab = 'functional'">
                功能障碍 <span class="tab-badge">{{ functionalIssues.length }}</span>
              </button>
              <button class="tab-btn" :class="{ active: activeTab === 'interaction' }" @click="activeTab = 'interaction'">
                交互体验 <span class="tab-badge">{{ interactionIssues.length }}</span>
              </button>
              <button class="tab-btn" :class="{ active: activeTab === 'visual' }" @click="activeTab = 'visual'">
                视觉一致性 <span class="tab-badge">{{ visualIssues.length }}</span>
              </button>
              <button
                type="button"
                class="tab-btn"
                :class="{ active: activeTab === 'content' }"
                title="检测全局文案风格是否一致，以及同类功能下提示、弹窗等用语是否统一"
                @click="activeTab = 'content'"
              >
                文案与话术 <span class="tab-badge">{{ contentIssues.length }}</span>
              </button>
              <span class="tab-divider" aria-hidden="true"></span>
              <div class="urgency-group">
                <button type="button" class="urgency-btn urgency-high" :class="{ 'is-active': activeUrgency === 'high' }" @click="toggleUrgency('high')">
                  高
                </button>
                <button type="button" class="urgency-btn urgency-medium" :class="{ 'is-active': activeUrgency === 'medium' }" @click="toggleUrgency('medium')">
                  中
                </button>
                <button type="button" class="urgency-btn urgency-low" :class="{ 'is-active': activeUrgency === 'low' }" @click="toggleUrgency('low')">
                  低
                </button>
              </div>
            </div>
            <div v-if="ignoredIssues.length > 0" class="ignored-bar">
              <span class="ignored-hint">已忽略 {{ ignoredIssues.length }} 项</span>
              <button type="button" class="ignored-toggle" @click="showIgnored = !showIgnored">{{ showIgnored ? '隐藏已忽略' : '查看已忽略' }}</button>
              <button type="button" class="ignored-restore-all" @click="restoreAllIgnored">全部恢复</button>
            </div>
          </div>

          <div class="issue-card" :class="{ 'issue-card--ignored': ignoredIds.has(issue.id) }" v-for="issue in pagedIssues" :key="issue.id">
            <div class="issue-card-row">
              <div class="issue-thumb" @click="openPreview(issue)">
                <span class="thumb-mode-badge">{{ currentModeName }}</span>
                <div
                  v-if="reportData.screenshot && issue.rect"
                  class="real-thumb-crop"
                  :style="getThumbStyle(issue.rect)"
                >
                  <div class="real-thumb-box" :style="getThumbBoxStyle(issue.rect)"></div>
                </div>
                <div v-else class="issue-thumb-inner">
                  <div class="tb tb-light"></div>
                  <div class="tb tb-red"></div>
                  <div class="tb tb-light"></div>
                </div>
                <div class="issue-thumb-footer no-print">点击放大查看</div>
              </div>
              <div class="issue-body">
                <div class="issue-badge-row">
                  <span class="issue-badge" :class="getUrgencyMeta(issue).badgeClass">
                    {{ getUrgencyMeta(issue).label }}
                  </span>
                  <span class="issue-tag" :style="{ background: getIssueTag(issue).bg, color: getIssueTag(issue).color }">{{ getIssueTag(issue).label }}</span>
                  <span class="issue-assignee">{{ getCategoryLabel(issue) }}</span>
                  <button type="button" class="ignore-btn no-print" @click="toggleIgnore(issue.id)">
                    {{ ignoredIds.has(issue.id) ? '恢复' : '忽略' }}
                  </button>
                </div>
                <div class="issue-title">{{ issue.title }}</div>
                <div class="issue-desc">{{ formatIssueDisplay(issue.desc) }}</div>
                <div class="issue-fix">
                  <div class="issue-fix-label">修复建议：</div>
                  <div class="issue-fix-text">{{ formatIssueDisplay(issue.suggestion) }}</div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="filteredIssues.length === 0" class="empty-state">
            当前分类下暂无问题。
          </div>

          <div v-if="filteredIssues.length > 0" class="issue-pagination no-print">
            <div class="pagination-row">
              <span class="pagination-total">共 {{ filteredIssues.length }} 条</span>
              <label class="pagination-size">
                每页
                <select v-model.number="issuePageSize" class="pagination-select">
                  <option v-for="n in issuePageSizeOptions" :key="n" :value="n">{{ n }}</option>
                </select>
                条
              </label>
              <div class="pagination-nav">
                <button type="button" class="pagination-btn" :disabled="issuePage <= 1" @click="issuePage--">上一页</button>
                <span class="pagination-pages">第 {{ issuePage }} / {{ issueTotalPages }} 页</span>
                <button type="button" class="pagination-btn" :disabled="issuePage >= issueTotalPages" @click="issuePage++">下一页</button>
              </div>
              <div class="pagination-jump">
                <span class="pagination-jump-lbl">跳转</span>
                <input
                  v-model="jumpPageInput"
                  type="text"
                  inputmode="numeric"
                  class="pagination-input"
                  :placeholder="'1-' + issueTotalPages"
                  @keyup.enter="jumpToIssuePage"
                />
                <button type="button" class="pagination-btn pagination-btn-go" @click="jumpToIssuePage">确定</button>
              </div>
            </div>
          </div>

          <div v-if="showIgnored && ignoredIssues.length > 0" class="ignored-section no-print">
            <div class="ignored-section-title">已忽略的问题（{{ ignoredIssues.length }}）</div>
            <div class="issue-card issue-card--ignored" v-for="issue in ignoredIssues" :key="'ign-' + issue.id">
              <div class="issue-card-row">
                <div class="issue-body">
                  <div class="issue-badge-row">
                    <span class="issue-badge" :class="getUrgencyMeta(issue).badgeClass">{{ getUrgencyMeta(issue).label }}</span>
                    <span class="issue-tag" :style="{ background: getIssueTag(issue).bg, color: getIssueTag(issue).color }">{{ getIssueTag(issue).label }}</span>
                    <span class="issue-assignee">{{ getCategoryLabel(issue) }}</span>
                    <button type="button" class="ignore-btn ignore-btn--restore" @click="toggleIgnore(issue.id)">恢复</button>
                  </div>
                  <div class="issue-title">{{ issue.title }}</div>
                  <div class="issue-desc">{{ formatIssueDisplay(issue.desc) }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-if="previewIssue && reportData" class="preview-overlay" @click.self="previewIssue = null">
    <div class="preview-modal">
      <div class="preview-header">
        <span class="preview-mode-badge">{{ currentModeName }}</span>
        <span class="preview-title">{{ previewIssue.title }}</span>
        <button class="preview-close" @click="previewIssue = null">X</button>
      </div>
      <div class="preview-body">
        <div
          v-if="reportData.screenshot && previewIssue.rect"
          class="preview-crop"
          :style="getPreviewStyle(previewIssue.rect)"
        >
          <div class="preview-box" :style="getPreviewBoxStyle(previewIssue.rect)"></div>
        </div>
        <div v-else class="preview-empty">暂无截图数据</div>
      </div>
      <div class="preview-footer">
        <span class="issue-tag" :style="{ background: getIssueTag(previewIssue).bg, color: getIssueTag(previewIssue).color }">{{ getIssueTag(previewIssue).label }}</span>
        <span class="preview-desc">{{ previewIssue.desc }}</span>
      </div>
    </div>
  </div>

  <Teleport to="body">
    <div v-if="exportModalOpen" class="export-modal-overlay" @click.self="closeExportModal">
      <div class="export-modal" role="dialog" aria-labelledby="export-modal-title" @click.stop>
        <h2 id="export-modal-title" class="export-modal-title">导出走查报告</h2>
        <p class="export-modal-hint">请选择导出格式。导出内容包含评分摘要、AI 结论、整页截图及各问题的局部标注截图。</p>
        <label class="export-modal-label" for="export-format-select">输出格式</label>
        <select id="export-format-select" v-model="exportFormat" class="export-modal-select" :disabled="exportLoading">
          <option value="pdf">PDF 文档</option>
          <option value="docx">Word 文档（.docx）</option>
          <option value="png">PNG 图片</option>
          <option value="jpg">JPG 图片</option>
        </select>
        <div v-if="exportLoading" class="export-modal-progress-wrap" role="status" aria-live="polite">
          <div class="export-modal-progress-text">{{ exportStepText }}</div>
          <div class="export-modal-progress-track">
            <div class="export-modal-progress-fill" :style="{ width: `${exportProgress}%` }"></div>
          </div>
          <div class="export-modal-progress-percent">{{ exportProgress }}%</div>
        </div>
        <div class="export-modal-actions">
          <button type="button" class="export-modal-btn export-modal-btn--ghost" :disabled="exportLoading" @click="closeExportModal">取消</button>
          <button type="button" class="export-modal-btn export-modal-btn--primary" :disabled="exportLoading" @click="confirmExport">
            {{ exportLoading ? '正在生成…' : '导出' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- 离屏渲染：供 html2canvas / Word 截图使用（无报告数据时不挂载，避免空引用） -->
  <div v-if="reportData" ref="exportPanelRef" class="report-export-panel" aria-hidden="true">
    <section class="rep-ex-page rep-ex-page--first">
      <h1 class="rep-ex-h1">自动化走查平台 · 走查报告</h1>
      <p class="rep-ex-line"><strong>目标页面：</strong>{{ reportData.url || '—' }}</p>
      <p class="rep-ex-line"><strong>走查模式：</strong>{{ currentModeName }}</p>
      <div class="rep-ex-top-cards">
        <div class="rpt-card score-card">
          <div class="score-card-hdg">页面规范性评分（{{ currentModeName }}）</div>
          <div class="score-body">
            <div class="ring-wrap">
              <svg class="ring-svg" width="110" height="110" viewBox="0 0 110 110">
                <circle class="ring-bg" cx="55" cy="55" r="44" />
                <circle class="ring-fg" cx="55" cy="55" r="44"
                  :stroke-dashoffset="276.5 - (276.5 * (displayScore || 0) / 100)"
                  stroke-dasharray="276.5" />
              </svg>
              <div class="ring-label">
                <div class="ring-score-line">
                  <span class="ring-pct">{{ displayScore || 0 }}</span><span class="ring-unit">分</span>
                </div>
                <span class="ring-sub">总评分</span>
              </div>
            </div>
            <div class="score-detail">
              <div class="score-badge" :class="scoreBadgeClass">{{ scoreBadgeText }}</div>
              <div class="score-desc">本次走查发现 {{ reportData.issueCount || 0 }} 个规范问题。建议优先修复高优问题。</div>
              <div class="score-stats">
                <div class="stat-block">
                  <div class="stat-val">{{ dimensionScores.functional }}<span class="stat-unit">分</span></div>
                  <div class="stat-label">功能障碍</div>
                </div>
                <div class="stat-block">
                  <div class="stat-val">{{ dimensionScores.interaction }}<span class="stat-unit">分</span></div>
                  <div class="stat-label">交互体验</div>
                </div>
                <div class="stat-block">
                  <div class="stat-val">{{ dimensionScores.visual }}<span class="stat-unit">分</span></div>
                  <div class="stat-label">视觉一致性</div>
                </div>
                <div class="stat-block">
                  <div class="stat-val">{{ dimensionScores.content }}<span class="stat-unit">分</span></div>
                  <div class="stat-label">文案与话术</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="rpt-card distribution-card">
          <div class="distribution-hd">关键问题分布</div>
          <div class="distribution-body">
            <div class="distribution-chart">
              <div class="chart-item" v-for="(item, idx) in topIssueCategories" :key="'ex-c-' + idx">
                <div class="chart-info">
                  <span class="chart-label">{{ item.name }}</span>
                  <span class="chart-count">{{ item.count }} 个问题 ({{ item.percentage }}%)</span>
                </div>
                <div class="chart-bar-wrap">
                  <div class="chart-bar" :style="{ width: item.percentage + '%', background: item.color }"></div>
                </div>
              </div>
            </div>
            <div class="distribution-summary">
              <div class="summary-label">AI 问题总结</div>
              <ul v-if="diagnosisExportHtmlList.length > 0" class="summary-bullets">
                <li v-for="(html, idx) in diagnosisExportHtmlList" :key="'diag-ex-' + idx" v-html="html"></li>
              </ul>
              <div v-else class="summary-text" v-html="diagnosisFallbackHtml"></div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section v-if="reportData.screenshot" class="rep-ex-page rep-ex-page--snapshot">
      <h2 class="rep-ex-subhd">实际页面快照</h2>
      <div class="rep-ex-snapshot-wrap">
        <img :src="screenshotSrc" class="rep-ex-full-img rep-ex-full-img--page" alt="" crossorigin="anonymous" />
      </div>
    </section>

    <section v-for="(issuePage, pageIdx) in exportIssuePages" :key="'ex-issue-page-' + pageIdx" class="rep-ex-page rep-ex-page--issue">
      <h2 class="rep-ex-subhd">问题清单（表格）</h2>
      <table class="rep-ex-table" cellspacing="0" cellpadding="0">
        <thead>
          <tr>
            <th class="col-index">序号</th>
            <th class="col-thumb">问题截图</th>
            <th class="col-title">问题标题</th>
            <th class="col-desc">问题描述</th>
            <th class="col-sug">修复建议</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in issuePage" :key="'ex-row-' + row.id">
            <td class="rep-ex-td-center">{{ row.index }}</td>
            <td>
              <img v-if="exportThumbMap[row.id]" :src="exportThumbMap[row.id]" class="rep-ex-thumb" alt="" />
              <span v-else class="rep-ex-thumb-empty">无截图</span>
            </td>
            <td>{{ row.title || '（无标题）' }}</td>
            <td>{{ row.desc || '—' }}</td>
            <td>{{ row.suggestion || '—' }}</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import AppNavbar from '../components/AppNavbar.vue'
import FilterSelect from '../components/FilterSelect.vue'
import { useAuditStore } from '../store/audit'
import { useUserStore } from '../store/user'
import axios from 'axios'
import { getCategoryType, getIssueUrgency as getUrgency } from '../utils/issueUrgency'
import { computeRestorationScore, RESTORATION_WEIGHTS } from '../utils/restorationScore'
import { splitDiagnosisLines, diagnosisMarkdownBoldToHtml } from '../utils/diagnosisFormat'
import { localizeCursorTermsInText } from '../utils/issueDisplayFormat'

function formatIssueDisplay(text) {
  return localizeCursorTermsInText(text == null ? '' : String(text))
}

const router = useRouter()
const auditStore = useAuditStore()
const userStore = useUserStore()
if (!auditStore.reportData) {
  auditStore.restoreReportFromSession()
}
const { reportData } = storeToRefs(auditStore)

/** AI 总结：分点 + **加粗** 渲染为 HTML */
const diagnosisBulletHtmlList = computed(() => {
  const raw = reportData.value?.diagnosis
  if (!raw || typeof raw !== 'string') return []
  const lines = splitDiagnosisLines(raw)
  return lines.map((line) => diagnosisMarkdownBoldToHtml(line))
})

const diagnosisFallbackHtml = computed(() => {
  const raw = reportData.value?.diagnosis
  if (!raw || typeof raw !== 'string' || !raw.trim()) return '暂无 AI 总结'
  return diagnosisMarkdownBoldToHtml(raw)
})

/** 导出面板内 AI 结论（支持 **加粗**） */
const diagnosisExportHtml = computed(() => diagnosisMarkdownBoldToHtml(reportData.value?.diagnosis || ''))
const diagnosisExportHtmlList = computed(() => {
  const raw = reportData.value?.diagnosis
  if (!raw || typeof raw !== 'string') return []
  return splitDiagnosisLines(raw).map((line) => diagnosisMarkdownBoldToHtml(line))
})

const exportModalOpen = ref(false)
const exportFormat = ref('pdf')
const exportLoading = ref(false)
const exportProgress = ref(0)
const exportStepText = ref('')
const exportThumbMap = ref({})
const exportPanelRef = ref(null)
const EXPORT_ISSUE_ROWS_PER_PAGE = 6

async function buildExportThumbMap(issues, screenshot, onItemDone) {
  if (!screenshot || !Array.isArray(issues) || issues.length === 0) return {}
  const { cropIssueFromScreenshot } = await import('../utils/reportExport')
  const map = {}
  const queue = issues.filter((i) => i?.rect)
  const total = queue.length || 1
  let done = 0
  // 限制并发，避免一次性占满内存导致导出长时间卡顿
  const workerSize = Math.min(6, queue.length)
  async function worker(startIdx) {
    for (let i = startIdx; i < queue.length; i += workerSize) {
      const issue = queue[i]
      const u = await cropIssueFromScreenshot(screenshot, issue.rect)
      if (u) map[issue.id] = u
      done += 1
      if (typeof onItemDone === 'function') onItemDone(done, total)
    }
  }
  await Promise.all(Array.from({ length: workerSize }, (_, idx) => worker(idx)))
  return map
}

const exportIssuePages = computed(() => {
  const rows = allIssues.value.map((issue, idx) => ({ ...issue, index: idx + 1 }))
  const pages = []
  for (let i = 0; i < rows.length; i += EXPORT_ISSUE_ROWS_PER_PAGE) {
    pages.push(rows.slice(i, i + EXPORT_ISSUE_ROWS_PER_PAGE))
  }
  return pages
})

const openExportModal = () => {
  exportModalOpen.value = true
}
const closeExportModal = () => {
  if (exportLoading.value) return
  exportModalOpen.value = false
}

async function confirmExport() {
  exportLoading.value = true
  exportProgress.value = 5
  exportStepText.value = '准备导出任务...'
  try {
    const issues = allIssues.value
    const {
      exportReportDocx,
      downloadPdfFromElement,
      downloadImageFromElement,
    } = await import('../utils/reportExport')
    exportProgress.value = 12
    exportStepText.value = '正在处理问题截图...'
    const map = await buildExportThumbMap(issues, reportData.value?.screenshot, (done, total) => {
      exportProgress.value = Math.min(62, 12 + Math.round((done / total) * 50))
    })
    exportThumbMap.value = map
    exportProgress.value = Math.max(exportProgress.value, 66)
    exportStepText.value = '正在排版导出内容...'
    await nextTick()
    await nextTick()
    const fmt = exportFormat.value
    const ts = Date.now()
    if (fmt === 'docx') {
      exportProgress.value = 78
      exportStepText.value = '正在生成 Word 文档...'
      await exportReportDocx({
        reportData: reportData.value,
        issues,
        diagnosisPlain: (reportData.value?.diagnosis || '').replace(/\*\*/g, ''),
        modeLabel: currentModeName.value,
        issueThumbMap: map,
        totalScore: displayScore.value,
      })
    } else {
      const el = exportPanelRef.value
      if (!el) throw new Error('export panel missing')
      exportProgress.value = 78
      exportStepText.value = fmt === 'pdf' ? '正在生成 PDF 文档...' : '正在生成图片文件...'
      if (fmt === 'pdf') await downloadPdfFromElement(el, `走查报告_${ts}.pdf`, {
        scale: 1.35,
        onProgress: (ratio) => {
          exportProgress.value = Math.min(98, 78 + Math.round(ratio * 20))
        },
      })
      else if (fmt === 'jpg') await downloadImageFromElement(el, 'image/jpeg', `走查报告_${ts}.jpg`)
      else await downloadImageFromElement(el, 'image/png', `走查报告_${ts}.png`)
    }
    exportProgress.value = 100
    exportStepText.value = '导出完成'
    exportModalOpen.value = false
  } catch (e) {
    console.error(e)
    alert('导出失败，请稍后再试')
  } finally {
    exportLoading.value = false
    exportProgress.value = 0
    exportStepText.value = ''
  }
}

const activeTab = ref('all')
/** null 表示不按紧急度筛选（显示当前分类下全部） */
const activeUrgency = ref(null)

const ignoredIds = ref(new Set())
const showIgnored = ref(false)
const toggleIgnore = (id) => {
  const s = new Set(ignoredIds.value)
  if (s.has(id)) s.delete(id); else s.add(id)
  ignoredIds.value = s
}
const restoreAllIgnored = () => { ignoredIds.value = new Set() }

const toggleUrgency = (level) => {
  activeUrgency.value = activeUrgency.value === level ? null : level
}
const trendRangeOptions = [
  { label: '近 1 周', value: '1w' },
  { label: '近 1 月', value: '1m' },
  { label: '近 3 月', value: '3m' },
  { label: '近半年', value: '6m' }
]
const trendRange = ref('1m')
const trendHistory = ref([])
const previewIssue = ref(null)
const TIP_GAP_PX = 2

function toValidDate(input) {
  if (!input) return null
  const d = new Date(input)
  return Number.isNaN(d.getTime()) ? null : d
}

function rangeStartDate(range) {
  const now = new Date()
  const start = new Date(now)
  if (range === '1w') start.setDate(now.getDate() - 6)
  else if (range === '1m') start.setDate(now.getDate() - 29)
  else if (range === '3m') start.setDate(now.getDate() - 89)
  else start.setDate(now.getDate() - 179)
  start.setHours(0, 0, 0, 0)
  return start
}

const trendData = computed(() => {
  if (!Array.isArray(trendHistory.value) || trendHistory.value.length === 0) return []
  const start = rangeStartDate(trendRange.value)
  const filtered = trendHistory.value
    .filter(item => item.dateObj && item.dateObj >= start)
    .sort((a, b) => a.dateObj - b.dateObj)
    .slice(-8)

  return filtered.map(item => ({
    score: item.score,
    tooltipDate: item.tooltipDate,
    rowKey: item.rowKey
  }))
})

/** 提示层贴问号：fixed 定位，与锚点水平居中，垂直方向与问号间隔 TIP_GAP_PX；必要时改为显示在问号下方 */
function positionTipNearIcon(anchorEl, popupEl, gap = TIP_GAP_PX) {
  if (!anchorEl || !popupEl) return {}
  const r = anchorEl.getBoundingClientRect()
  const ph = popupEl.offsetHeight
  const pw = popupEl.offsetWidth
  let top = r.top - ph - gap
  let placeAbove = true
  if (top < 8) {
    placeAbove = false
    top = r.bottom + gap
  }
  let left = r.left + r.width / 2 - pw / 2
  left = Math.max(8, Math.min(left, window.innerWidth - pw - 8))
  if (placeAbove) top = Math.max(8, top)
  else top = Math.min(top, window.innerHeight - ph - 8)
  return {
    position: 'fixed',
    top: `${Math.round(top)}px`,
    left: `${Math.round(left)}px`,
    zIndex: 10050,
  }
}

const showMainTip = ref(false)
const mainTipPopupRef = ref(null)
const mainTipStyle = ref({})
let mainTipTimer = null
const scheduleMainTipPosition = (anchorEl) => {
  nextTick(() => {
    nextTick(() => {
      const pop = mainTipPopupRef.value
      if (!anchorEl || !pop) return
      mainTipStyle.value = positionTipNearIcon(anchorEl, pop)
    })
  })
}
const enterMainTip = (e) => {
  clearTimeout(mainTipTimer)
  showMainTip.value = true
  if (e?.currentTarget) scheduleMainTipPosition(e.currentTarget)
}
const onMainTipPopupEnter = () => {
  clearTimeout(mainTipTimer)
}
const leaveMainTip = () => {
  mainTipTimer = setTimeout(() => {
    showMainTip.value = false
    mainTipStyle.value = {}
  }, 120)
}

const activeDimTip = ref(null)
const dimTipPopupRef = ref(null)
const dimTipStyle = ref({})
let dimTipTimer = null
const scheduleDimTipPosition = (anchorEl) => {
  nextTick(() => {
    nextTick(() => {
      const pop = dimTipPopupRef.value
      if (!anchorEl || !pop) return
      dimTipStyle.value = positionTipNearIcon(anchorEl, pop)
    })
  })
}
const enterDimTip = (key, e) => {
  clearTimeout(dimTipTimer)
  activeDimTip.value = key
  if (e?.currentTarget?.classList?.contains('score-tip-icon')) {
    scheduleDimTipPosition(e.currentTarget)
  }
}
const onDimTipPopupEnter = () => {
  clearTimeout(dimTipTimer)
}
const leaveDimTip = () => {
  dimTipTimer = setTimeout(() => {
    activeDimTip.value = null
    dimTipStyle.value = {}
  }, 120)
}

const dimTipLabels = { functional: '功能障碍', interaction: '交互体验', visual: '视觉一致性', content: '文案与话术' }
const dimTipLabel = computed(() => dimTipLabels[activeDimTip.value] || '')

function formatDed(v) {
  if (v == null || Number.isNaN(Number(v))) return '0.00'
  return Number(v).toFixed(2)
}

const getCategoryLabel = (issue) => {
  const labels = { visual: '视觉一致性', interaction: '交互体验', content: '文案与话术', functional: '功能障碍' }
  return labels[getCategoryType(issue?.category, issue)] || issue?.category
}

const urgencyMetaMap = {
  high: { label: '高', badgeClass: 'badge-high' },
  medium: { label: '中', badgeClass: 'badge-medium' },
  low: { label: '低', badgeClass: 'badge-low' }
}

const getUrgencyMeta = (issue) => urgencyMetaMap[getUrgency(issue)] || urgencyMetaMap.low

const issueTagMap = [
  { keywords: ['字体', '字号', '字阶', 'font'], label: '字体', bg: '#eef2ff', color: '#4338ca' },
  { keywords: ['颜色', '色盘', '色值', '品牌色', 'color'], label: '颜色', bg: '#fef2f2', color: '#dc2626' },
  { keywords: ['间距', 'margin', 'padding', 'spacing'], label: '间距', bg: '#f0fdf4', color: '#16a34a' },
  { keywords: ['圆角', 'radius'], label: '圆角', bg: '#fffbeb', color: '#d97706' },
  { keywords: ['行高', 'line-height'], label: '行高', bg: '#faf5ff', color: '#9333ea' },
  { keywords: ['字重', 'font-weight'], label: '字重', bg: '#eef2ff', color: '#4338ca' },
  { keywords: ['按钮', 'button', 'btn'], label: '按钮', bg: '#eff6ff', color: '#2563eb' },
  { keywords: ['输入框', 'input', '表单', '选择器'], label: '表单', bg: '#f0fdf4', color: '#16a34a' },
  { keywords: ['导航', 'nav', '分页'], label: '导航', bg: '#fefce8', color: '#ca8a04' },
  { keywords: ['点击', '热区', '光标', 'cursor'], label: '交互', bg: '#fff7ed', color: '#ea580c' },
  { keywords: ['对比度', '无障碍', 'alt', '标题层级'], label: '无障碍', bg: '#fdf2f8', color: '#db2777' },
  { keywords: ['投影', '阴影', 'shadow'], label: '阴影', bg: '#f5f3ff', color: '#7c3aed' },
  { keywords: ['动画', '过渡', 'transition'], label: '动效', bg: '#ecfeff', color: '#0891b2' },
  { keywords: ['栅格', 'grid', '容器'], label: '栅格', bg: '#f0f9ff', color: '#0284c7' },
  { keywords: ['图片', 'img', '体积'], label: '图片', bg: '#fefce8', color: '#ca8a04' },
  { keywords: ['中英文', '空格', '日期', '死链', '文案'], label: '文案', bg: '#f0fdf4', color: '#16a34a' },
  { keywords: ['布局', '溢出', '省略', 'z-index', '层级'], label: '布局', bg: '#fff1f2', color: '#e11d48' },
  { keywords: ['表格', 'table', '行高'], label: '表格', bg: '#f8fafc', color: '#475569' },
  { keywords: ['标签', 'tag'], label: '标签', bg: '#faf5ff', color: '#9333ea' }
]

const getIssueTag = (issue) => {
  const t = issue?.title || ''
  if (t.includes('图片体积过大')) {
    return { label: '资源', bg: '#fff7ed', color: '#c2410c' }
  }
  const text = (t + (issue.category || '')).toLowerCase()
  for (const rule of issueTagMap) {
    if (rule.keywords.some(kw => text.includes(kw))) {
      return rule
    }
  }
  return { label: '样式', bg: '#f3f4f6', color: '#6b7280' }
}

const currentModeName = computed(() => {
  const m = auditStore.checkMode
  if (m === 'baseline' || m === 'static_scan') return '基准值模式'
  if (m === 'design') return '设计稿模式'
  if (m === 'component') return '组件模式'
  return '基准值模式'
})

const rawIssues = computed(() => (reportData.value && reportData.value.issues ? reportData.value.issues : []))
const allIssues = computed(() => rawIssues.value.filter(i => !ignoredIds.value.has(i.id)))
const ignoredIssues = computed(() => rawIssues.value.filter(i => ignoredIds.value.has(i.id)))

const visualIssues = computed(() => allIssues.value.filter(i => getCategoryType(i.category, i) === 'visual'))
const interactionIssues = computed(() => allIssues.value.filter(i => getCategoryType(i.category, i) === 'interaction'))
const contentIssues = computed(() => allIssues.value.filter(i => getCategoryType(i.category, i) === 'content'))
const functionalIssues = computed(() => allIssues.value.filter(i => getCategoryType(i.category, i) === 'functional'))

const categoryFilteredIssues = computed(() => {
  if (activeTab.value === 'visual') return visualIssues.value
  if (activeTab.value === 'interaction') return interactionIssues.value
  if (activeTab.value === 'content') return contentIssues.value
  if (activeTab.value === 'functional') return functionalIssues.value
  return allIssues.value
})

const urgencyCounts = computed(() => ({
  high: categoryFilteredIssues.value.filter(i => getUrgency(i) === 'high').length,
  medium: categoryFilteredIssues.value.filter(i => getUrgency(i) === 'medium').length,
  low: categoryFilteredIssues.value.filter(i => getUrgency(i) === 'low').length
}))

const issuePageSizeOptions = [10, 20, 50, 100]
const issuePageSize = ref(20)
const issuePage = ref(1)
const jumpPageInput = ref('')

watch(activeTab, () => {
  issuePage.value = 1
  if (activeUrgency.value !== null && urgencyCounts.value[activeUrgency.value] === 0) {
    activeUrgency.value = null
  }
})

watch(activeUrgency, () => {
  issuePage.value = 1
})

const filteredIssues = computed(() => {
  if (activeUrgency.value === null) return categoryFilteredIssues.value
  return categoryFilteredIssues.value.filter(i => getUrgency(i) === activeUrgency.value)
})

const issueTotalPages = computed(() => {
  const total = filteredIssues.value.length
  if (total === 0) return 1
  return Math.ceil(total / issuePageSize.value)
})

const pagedIssues = computed(() => {
  const list = filteredIssues.value
  const size = issuePageSize.value
  const maxPage = Math.max(1, Math.ceil(list.length / size) || 1)
  const page = Math.min(Math.max(1, issuePage.value), maxPage)
  const start = (page - 1) * size
  return list.slice(start, start + size)
})

watch(issuePageSize, () => {
  issuePage.value = 1
})

watch([filteredIssues, issuePageSize], () => {
  const total = filteredIssues.value.length
  const maxPage = Math.max(1, Math.ceil(total / issuePageSize.value) || 1)
  if (issuePage.value > maxPage) issuePage.value = maxPage
}, { deep: true })

const jumpToIssuePage = () => {
  const raw = String(jumpPageInput.value).trim()
  if (!raw) return
  const p = parseInt(raw, 10)
  if (Number.isNaN(p) || p < 1) return
  issuePage.value = Math.min(p, issueTotalPages.value)
  jumpPageInput.value = ''
}

const countByLevel = (issues) => {
  const h = issues.filter(i => i.level === 'high').length
  const m = issues.filter(i => i.level === 'medium').length
  const l = issues.filter(i => i.level === 'low' || i.level === 'warning').length
  return { h, m, l }
}

const restorationDisplay = computed(() =>
  computeRestorationScore(allIssues.value, reportData.value?.checkItemTotal)
)
const displayScore = computed(() => restorationDisplay.value.score)
const dimensionScores = computed(() => restorationDisplay.value.dimensionScores)
const restorationTotalDeduction = computed(() => {
  const d = restorationDisplay.value.dimensionDeductions
  return (d.functional || 0) + (d.interaction || 0) + (d.visual || 0) + (d.content || 0)
})

const scoreBadgeClass = computed(() => {
  const s = displayScore.value
  if (s >= 90) return 'badge-good'
  if (s >= 70) return 'badge-ok'
  return 'badge-bad'
})

const scoreBadgeText = computed(() => {
  const s = displayScore.value
  if (s >= 90) return '表现优秀，基本符合规范'
  if (s >= 70) return '存在部分偏差，建议修复'
  return '偏离度较高，需重点整改'
})

const activeDimWeight = computed(() =>
  activeDimTip.value ? RESTORATION_WEIGHTS[activeDimTip.value] : 0
)
const activeDimCount = computed(() =>
  activeDimTip.value ? restorationDisplay.value.dimensionCounts[activeDimTip.value] : 0
)
const activeDimDeduction = computed(() =>
  activeDimTip.value ? restorationDisplay.value.dimensionDeductions[activeDimTip.value] : 0
)
const ringDashOffset = computed(() => {
  const C = 276.5
  const gapPx = 6
  const s = Math.max(0, Math.min(100, Number(displayScore.value) || 0))
  const fill = Math.min(C - gapPx, (C * s) / 100)
  return C - fill
})

const scoreBreakdown = computed(() => ({
  all: countByLevel(allIssues.value),
  visual: countByLevel(visualIssues.value),
  interaction: countByLevel(interactionIssues.value),
  content: countByLevel(contentIssues.value),
  functional: countByLevel(functionalIssues.value)
}))

const topIssueCategories = computed(() => {
  const counts = {}
  allIssues.value.forEach(i => {
    const t = getCategoryType(i.category, i)
    counts[t] = (counts[t] || 0) + 1
  })
  const total = allIssues.value.length || 1
  const cats = [
    { name: '视觉一致性', key: 'visual', color: '#1A6AFF' },
    { name: '交互体验', key: 'interaction', color: '#f59e0b' },
    { name: '文案与话术', key: 'content', color: '#10b981' },
    { name: '功能障碍', key: 'functional', color: '#ef4444' }
  ]
  return cats
    .map(c => ({
      name: c.name,
      count: counts[c.key] || 0,
      percentage: Math.round(((counts[c.key] || 0) / total) * 100),
      color: c.color
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 4)
})

const formattedUrl = computed(() => {
  const u = reportData.value && reportData.value.url
  if (u == null || typeof u !== 'string') return ''
  const t = u.trim()
  if (!t) return ''
  if (/^https?:\/\//i.test(t)) return t
  return 'https://' + t
})

const screenshotSrc = computed(() => {
  if (!reportData.value || !reportData.value.screenshot) return ''
  return 'data:image/png;base64,' + reportData.value.screenshot
})

onMounted(async () => {
  if (!reportData.value) {
    auditStore.restoreReportFromSession()
  }
  if (!reportData.value) {
    return
  }
  if (reportData.value.mode) {
    auditStore.setCheckMode(reportData.value.mode)
  }
  if (userStore.userInfo) {
    try {
      const res = await axios.get('http://localhost:8000/api/history/' + userStore.userInfo.id)
      if (res.data.status === 'success') {
        const history = res.data.data
        if (history && history.length > 0) {
          trendHistory.value = history
            .map((h, i) => {
              const dateObj = toValidDate(h.created_at)
              if (!dateObj) return null
              const y = dateObj.getFullYear()
              const month = String(dateObj.getMonth() + 1).padStart(2, '0')
              const day = String(dateObj.getDate()).padStart(2, '0')
              return {
                score: Number.isFinite(Number(h.score)) ? Number(h.score) : 0,
                tooltipDate: `${y}-${month}-${day}`,
                rowKey: h.id != null ? `h-${h.id}` : `t-${h.created_at || i}`,
                dateObj
              }
            })
            .filter(Boolean)
        }
      }
    } catch (e) {
      console.error('trend data error', e)
    }
  }
})

const goTo = (path) => router.push(path)
const openPreview = (issue) => { previewIssue.value = issue }

const THUMB_PAD = 80
const getThumbStyle = (rect) => {
  const x = Math.max(0, rect.left - THUMB_PAD)
  const y = Math.max(0, rect.top - THUMB_PAD)
  return {
    backgroundImage: 'url(' + screenshotSrc.value + ')',
    backgroundPosition: '-' + x + 'px -' + y + 'px'
  }
}
const getThumbBoxStyle = (rect) => {
  const xOff = rect.left < THUMB_PAD ? rect.left : THUMB_PAD
  const yOff = rect.top < THUMB_PAD ? rect.top : THUMB_PAD
  return {
    top: yOff + 'px',
    left: xOff + 'px',
    width: rect.width + 'px',
    height: rect.height + 'px'
  }
}

const PREVIEW_PAD = 150
const getPreviewStyle = (rect) => {
  const x = Math.max(0, rect.left - PREVIEW_PAD)
  const y = Math.max(0, rect.top - PREVIEW_PAD)
  return {
    backgroundImage: 'url(' + screenshotSrc.value + ')',
    backgroundPosition: '-' + x + 'px -' + y + 'px',
    width: (rect.width + PREVIEW_PAD * 2) + 'px',
    height: (rect.height + PREVIEW_PAD * 2) + 'px'
  }
}
const getPreviewBoxStyle = (rect) => {
  const xOff = rect.left < PREVIEW_PAD ? rect.left : PREVIEW_PAD
  const yOff = rect.top < PREVIEW_PAD ? rect.top : PREVIEW_PAD
  return {
    top: yOff + 'px',
    left: xOff + 'px',
    width: rect.width + 'px',
    height: rect.height + 'px'
  }
}
</script>

<style scoped>
.rpt-body { background: #f4f6fb; min-height: 100vh; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif; }
.rpt-page { padding-top: 80px; padding-bottom: 60px; }
.rpt-inner { max-width: 1080px; margin: 0 auto; padding: 0 24px; }
.rpt-breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.85rem; color: #9ca3af; margin-bottom: 22px; }
.rpt-breadcrumb a { color: #6b7280; text-decoration: none; }
.rpt-breadcrumb a:hover { color: #1A6AFF; }
.rpt-breadcrumb .cur { color: #1a1d2e; font-weight: 500; }
.rpt-page-stack { width: 100%; }
.rpt-head-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}
.rpt-head-title {
  margin: 0;
  font-size: 26px;
  line-height: 1.2;
  font-weight: 800;
  color: #1a1d2e;
}
.rpt-head-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.rpt-top-row {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 20px;
  align-items: start;
}
.rpt-left-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
}
.rpt-left-stack > .rpt-card { margin-bottom: 0; }
.rpt-issues-section {
  width: 100%;
  margin-top: 20px;
  min-width: 0;
  background: #fff;
  border: 1px solid #e8eaf0;
  border-radius: 14px;
  box-shadow: 0 1px 4px rgba(60,72,120,.06);
  padding: 16px 16px 14px;
  box-sizing: border-box;
}
.btn { border: none; font-family: inherit; cursor: pointer; transition: all 0.2s; font-weight: 600; }
.btn-primary { background: #1A6AFF; color: white; border-radius: 6px; height: 36px; padding: 0 16px; font-size: 0.85rem; display: inline-flex; align-items: center; box-sizing: border-box; }
.btn-primary:hover { background: #1557e6; }
.btn-ghost { background: transparent; color: #6b7280; border: 1px solid #e8eaf0; border-radius: 6px; height: 36px; padding: 0 16px; font-size: 0.85rem; display: inline-flex; align-items: center; box-sizing: border-box; }
.btn-ghost:hover { background: #f9fafb; color: #1a1d2e; }
.rpt-card { background: #fff; border: 1px solid #e8eaf0; border-radius: 14px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(60,72,120,.04); overflow: hidden; }
.score-card { padding: 0 24px 22px; }
.score-card.score-tip-anchor { min-height: 228px; box-sizing: border-box; }
.score-card-hdg {
  margin: 0 -24px 18px;
  padding: 14px 20px;
  font-weight: 700;
  font-size: 0.9rem;
  background: #fafbff;
  border-bottom: 1px solid #f0f1f6;
  color: #1a1d2e;
}

.score-tip-anchor { position: relative; }
.score-tip-wrap { position: relative; }
.score-tip-icon {
  display: inline-flex; align-items: center; justify-content: center;
  width: 18px; height: 18px; border-radius: 50%;
  background: #e8eaf0; color: #6b7280; font-size: 11px; font-weight: 700;
  cursor: help; margin-left: 6px; vertical-align: middle;
  transition: background 0.15s, color 0.15s;
}
.score-tip-icon.sm { width: 14px; height: 14px; font-size: 9px; margin-left: 4px; }
.score-tip-icon:hover { background: #1A6AFF; color: #fff; }
.score-tip-popup {
  background: #1a1d2e; color: #fff; border-radius: 10px;
  padding: 14px 18px; min-width: 280px; max-width: min(360px, calc(100vw - 16px));
  box-shadow: 0 8px 24px rgba(0,0,0,0.22);
  font-size: 0.78rem; line-height: 1.6;
  pointer-events: auto;
  box-sizing: border-box;
}
.score-tip-popup--fixed {
  margin: 0;
  transform: none;
}
.tip-fade-enter-active, .tip-fade-leave-active { transition: opacity 0.2s ease; }
.tip-fade-enter-from, .tip-fade-leave-to { opacity: 0; }
.score-tip-title { font-weight: 700; margin-bottom: 6px; font-size: 0.82rem; color: #dbeafe; }
.score-tip-formula { font-family: 'SF Mono', 'Menlo', monospace; font-size: 0.76rem; background: rgba(255,255,255,0.08); padding: 6px 10px; border-radius: 6px; margin-bottom: 8px; color: #93c5fd; word-break: break-all; }
.score-tip-detail { display: flex; flex-direction: column; gap: 2px; color: #d1d5db; font-size: 0.74rem; }
.score-body { display: flex; align-items: flex-start; gap: 28px; }
.ring-wrap { position: relative; width: 110px; height: 110px; flex-shrink: 0; }
.ring-svg { transform: rotate(-90deg); }
.ring-bg { fill: none; stroke: #eef2ff; stroke-width: 10; }
.ring-fg { fill: none; stroke: #1A6AFF; stroke-width: 10; stroke-linecap: round; transition: stroke-dashoffset 1s ease; }
.ring-label { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.ring-score-line { display: inline-flex; align-items: baseline; justify-content: center; gap: 2px; line-height: 1; }
.ring-pct { font-size: 24px; font-weight: 800; color: #1A6AFF; line-height: 1; }
.ring-unit { font-size: 13px; font-weight: 700; color: #1A6AFF; line-height: 1; }
.ring-sub { font-size: 0.68rem; color: #9ca3af; margin-top: 3px; }
.score-detail { flex: 1; }
.score-badge { display: inline-flex; padding: 4px 12px; border-radius: 99px; font-size: 0.78rem; font-weight: 600; margin-bottom: 12px; }
.badge-good { background: #d1fae5; color: #065f46; }
.badge-ok { background: #fef3c7; color: #92400e; }
.badge-bad { background: #fee2e2; color: #991b1b; }
.score-desc { font-size: 0.86rem; color: #6b7280; line-height: 1.75; margin-bottom: 18px; }
.score-stats { display: flex; gap: 20px; align-items: flex-start; flex-wrap: wrap; }
.stat-block { flex: 1; min-width: 80px; }
.stat-val { font-size: 1.2rem; font-weight: 800; color: #1a1d2e; display: inline-flex; align-items: baseline; gap: 2px; }
.stat-unit { font-size: 0.72em; font-weight: 700; color: #6b7280; }
.stat-label { font-size: 0.75rem; color: #9ca3af; margin-top: 4px; }
.distribution-card {
  padding: 0 24px 22px;
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.distribution-hd {
  margin: 0 -24px 18px;
  padding: 14px 20px;
  font-weight: 700;
  font-size: 0.9rem;
  background: #fafbff;
  border-bottom: 1px solid #f0f1f6;
  color: #1a1d2e;
  flex-shrink: 0;
}
.distribution-body { display: flex; flex-direction: column; gap: 20px; flex: 1; min-height: 0; }
.distribution-chart { display: flex; flex-direction: column; gap: 24px; }
.chart-item { display: flex; flex-direction: column; gap: 8px; }
.chart-bar-wrap { width: 100%; height: 8px; background: #f3f4f6; border-radius: 4px; overflow: hidden; }
.chart-bar { height: 100%; border-radius: 4px; transition: width 0.5s ease; }
.chart-info { display: flex; justify-content: space-between; align-items: center; }
.chart-label { font-size: 0.85rem; font-weight: 600; color: #1a1d2e; }
.chart-count { font-size: 0.8rem; color: #6b7280; }
.distribution-summary {
  background: #f8faff;
  border-left: 3px solid #1A6AFF;
  padding: 14px 16px;
  border-radius: 0 8px 8px 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 120px;
}
.summary-label { font-size: 0.75rem; color: #1A6AFF; font-weight: 700; margin-bottom: 8px; flex-shrink: 0; }
.summary-text { font-size: 0.85rem; color: #4b5563; line-height: 1.6; flex: 1; min-height: 4em; overflow-y: auto; }
.summary-bullets {
  margin: 0;
  padding-left: 1.2em;
  font-size: 0.85rem;
  color: #4b5563;
  line-height: 1.65;
  flex: 1;
  min-height: 4em;
  overflow-y: auto;
  list-style-type: disc;
}
.summary-bullets li { margin-bottom: 10px; padding-left: 2px; }
.summary-bullets li:last-child { margin-bottom: 0; }
.summary-bullets li :deep(strong) { font-weight: 700; color: #1a1d2e; }
.summary-text :deep(strong) { font-weight: 700; color: #1a1d2e; }
.issue-list-hd {
  margin: -16px -16px 10px;
  padding: 14px 20px;
  font-weight: 700;
  font-size: 0.9rem;
  background: #fafbff;
  border-bottom: 1px solid #f0f1f6;
  color: #1a1d2e;
}
.issue-list-title { font-weight: 700; font-size: 1rem; color: #1a1d2e; }
.issue-list-cnt { background: #f3f4f6; color: #6b7280; font-size: 0.78rem; font-weight: 600; padding: 2px 8px; border-radius: 99px; margin-left: 6px; }
.issue-tabs-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  row-gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 0;
  border-bottom: 1px solid #e8eaf0;
}
.issue-tabs-main {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  flex: 1 1 0;
  min-width: 0;
}
.tab-btn { height: 40px; padding: 0 16px; border: none; background: transparent; font-size: 0.85rem; color: #6b7280; cursor: pointer; transition: color 0.2s, border-color 0.2s; font-weight: 600; border-bottom: 2px solid transparent; margin-bottom: -1px; display: inline-flex; align-items: center; box-sizing: border-box; flex-shrink: 0; white-space: nowrap; }
.tab-btn:hover { color: #1A6AFF; }
.tab-btn.active { color: #1A6AFF; border-bottom-color: #1A6AFF; }
.tab-badge { display: inline-block; background: #f3f4f6; color: #6b7280; font-size: 0.7rem; padding: 2px 6px; border-radius: 99px; margin-left: 6px; font-weight: 600; }
.tab-btn.active .tab-badge { background: #dbeafe; color: #1A6AFF; }
.tab-divider { width: 1px; height: 14px; background: #e5e7eb; margin: 0 6px 0 2px; flex-shrink: 0; align-self: center; }
.urgency-group {
  display: inline-flex;
  align-items: center;
  gap: 16px;
  flex-shrink: 0;
  margin-left: 4px;
}
.urgency-btn {
  box-sizing: border-box;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 22px;
  min-width: 28px;
  padding: 0 10px;
  border: none;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 700;
  line-height: 1;
  color: #fff;
  cursor: pointer;
  flex-shrink: 0;
  align-self: center;
  margin-bottom: -2px;
  opacity: 0.72;
  transform: scale(1);
  transition: opacity 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}
.urgency-btn:hover,
.urgency-btn:focus-visible {
  color: #fff;
  outline: none;
  opacity: 1;
}
.urgency-btn.is-active {
  color: #fff;
  outline: none;
  opacity: 1;
  animation: urgency-active-glow 1.25s ease-in-out infinite;
}
@keyframes urgency-active-glow {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.45);
  }
  50% {
    transform: scale(1.08);
    box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.55), 0 4px 10px rgba(0, 0, 0, 0.12);
  }
}
.urgency-btn:focus-visible { box-shadow: 0 0 0 2px rgba(26, 106, 255, 0.35); }
.urgency-btn.is-active:focus-visible { animation: urgency-active-glow 1.25s ease-in-out infinite; }
.urgency-high { background: #ef4444; }
.urgency-high:hover,
.urgency-high:focus-visible,
.urgency-high.is-active { background: #ef4444; }
.urgency-medium { background: #fbbf24; }
.urgency-medium:hover,
.urgency-medium:focus-visible,
.urgency-medium.is-active { background: #fbbf24; }
.urgency-low { background: #3b82f6; }
.urgency-low:hover,
.urgency-low:focus-visible,
.urgency-low.is-active { background: #3b82f6; }
.issue-card { background: #fff; border: 1px solid #e8eaf0; border-radius: 12px; overflow: hidden; margin: 0 8px 16px; box-shadow: 0 1px 3px rgba(60,72,120,.05); transition: transform 0.2s, box-shadow 0.2s; }
.issue-card:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(60,72,120,.08); }
.issue-card-row { display: flex; }
.issue-thumb { width: 200px; background: #f3f4f6; position: relative; display: flex; align-items: center; justify-content: center; cursor: pointer; overflow: hidden; flex-shrink: 0; }
.thumb-mode-badge { position: absolute; top: 8px; right: 8px; font-size: 0.6rem; background: rgba(0,0,0,.6); color: #fff; padding: 2px 8px; border-radius: 4px; font-weight: 600; z-index: 10; }
.real-thumb-crop { width: 100%; height: 100%; position: absolute; inset: 0; background-repeat: no-repeat; z-index: 1; }
.real-thumb-box { position: absolute; border: 2px solid #ef4444; background: rgba(239,68,68,0.15); box-shadow: 0 0 0 2000px rgba(0,0,0,0.35); border-radius: 2px; }
.issue-thumb-inner { width: 78%; display: flex; gap: 6px; z-index: 5; }
.tb { height: 30px; border-radius: 5px; }
.tb-light { background: rgba(255,255,255,.55); flex: 1; }
.tb-red { border: 2px solid rgba(239,68,68,.8); background: rgba(239,68,68,.08); flex: 1.5; }
.issue-thumb-footer { position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,.5); color: #fff; font-size: 0.7rem; text-align: center; padding: 5px 0; z-index: 10; }
.issue-thumb:hover .issue-thumb-footer { background: rgba(26, 106, 255,.8); }
.preview-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.6); z-index: 9999; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(4px); }
.preview-modal { background: #fff; border-radius: 14px; max-width: 80vw; max-height: 85vh; overflow: hidden; box-shadow: 0 24px 50px rgba(0,0,0,.3); display: flex; flex-direction: column; }
.preview-header { display: flex; align-items: center; gap: 12px; padding: 16px 20px; border-bottom: 1px solid #e8eaf0; }
.preview-mode-badge { font-size: 0.7rem; background: #1A6AFF; color: #fff; padding: 3px 10px; border-radius: 4px; font-weight: 600; }
.preview-title { font-weight: 700; font-size: 1rem; color: #1a1d2e; flex: 1; }
.preview-close { background: none; border: none; font-size: 1.1rem; cursor: pointer; color: #9ca3af; padding: 4px 8px; border-radius: 4px; }
.preview-close:hover { background: #f3f4f6; color: #1a1d2e; }
.preview-body { overflow: auto; padding: 20px; display: flex; justify-content: center; background: #f4f6fb; }
.preview-crop { position: relative; background-repeat: no-repeat; border-radius: 8px; border: 1px solid #e8eaf0; flex-shrink: 0; }
.preview-box { position: absolute; border: 2px solid #ef4444; background: rgba(239,68,68,0.12); box-shadow: 0 0 0 2000px rgba(0,0,0,0.25); border-radius: 2px; }
.preview-empty { padding: 60px; text-align: center; color: #9ca3af; }
.preview-footer { padding: 14px 20px; border-top: 1px solid #e8eaf0; display: flex; align-items: center; gap: 12px; }
.preview-desc { font-size: 0.85rem; color: #6b7280; }
.issue-body { flex: 1; padding: 20px 24px; display: flex; flex-direction: column; gap: 8px; }
.issue-badge-row { display: flex; align-items: center; gap: 12px; }
.issue-badge { display: inline-flex; align-items: center; gap: 4px; font-size: 0.7rem; font-weight: 800; padding: 3px 10px; border-radius: 4px; letter-spacing: .04em; color: white; }
.badge-high { background: #ef4444; }
.badge-medium { background: #fbbf24; color: #fff; }
.badge-low { background: #3b82f6; }
.issue-assignee { font-size: 0.78rem; color: #9ca3af; font-weight: 500; }
.issue-tag { font-size: 0.7rem; font-weight: 600; padding: 2px 8px; border-radius: 4px; white-space: nowrap; }
.issue-title { font-weight: 700; font-size: 1rem; color: #1a1d2e; }
.issue-desc { font-size: 0.85rem; color: #6b7280; line-height: 1.6; }
.issue-fix { background: #f8faff; border-left: 3px solid #1A6AFF; padding: 10px 14px; margin-top: 4px; border-radius: 0 6px 6px 0; }
.issue-fix-label { font-size: 0.75rem; color: #1A6AFF; font-weight: 700; margin-bottom: 4px; }
.issue-fix-text { font-size: 0.8rem; font-family: monospace; color: #4b5563; }

.ignore-btn {
  margin-left: auto;
  padding: 0 10px;
  height: 26px;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  background: #f9fafb;
  color: #6b7280;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
}
.issue-card:hover .ignore-btn { opacity: 1; pointer-events: auto; }
.ignore-btn:hover { background: #eef2ff; color: #1A6AFF; border-color: #93b4fd; }
.ignore-btn--restore { opacity: 1; pointer-events: auto; }
.ignore-btn--restore:hover { background: #dbeafe; color: #1d4ed8; border-color: #93c5fd; }
.issue-card--ignored { opacity: 0.55; }

.ignored-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  margin-left: auto;
  font-size: 0.8rem;
  white-space: nowrap;
}
.ignored-hint { color: #9ca3af; }
.ignored-toggle, .ignored-restore-all {
  padding: 0 8px;
  height: 26px;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  background: #f9fafb;
  color: #6b7280;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
}
.ignored-toggle:hover { background: #eef2ff; color: #4338ca; border-color: #a5b4fc; }
.ignored-restore-all:hover { background: #dbeafe; color: #1d4ed8; border-color: #93c5fd; }
.ignored-section { margin-top: 16px; }
.ignored-section-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: #9ca3af;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px dashed #e5e7eb;
}

.empty-state { text-align: center; padding: 40px; color: #9ca3af; background: white; border-radius: 12px; border: 1px solid #e8eaf0; }
.issue-pagination { margin: 8px 8px 0; padding: 16px 18px; background: #fff; border: 1px solid #e8eaf0; border-radius: 12px; box-shadow: 0 1px 3px rgba(60,72,120,.05); }
.pagination-row { display: flex; flex-wrap: wrap; align-items: center; gap: 14px 20px; font-size: 0.82rem; color: #6b7280; }
.pagination-total { font-weight: 600; color: #4b5563; }
.pagination-size { display: inline-flex; align-items: center; gap: 6px; cursor: pointer; }
.pagination-select { border: 1px solid #e8eaf0; border-radius: 6px; height: 32px; padding: 0 28px 0 10px; font-size: 14px; font-weight: 400; font-family: inherit; color: #1a1d2e; background: #fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%236b7280' d='M3 4.5L6 7.5L9 4.5'/%3E%3C/svg%3E") no-repeat right 8px center; cursor: pointer; appearance: none; box-sizing: border-box; }
.pagination-select:hover { border-color: #c7d2fe; }
.pagination-nav { display: inline-flex; align-items: center; gap: 10px; }
.pagination-pages { font-weight: 600; color: #1a1d2e; min-width: 7em; text-align: center; }
.pagination-btn { border: 1px solid #e8eaf0; background: #fff; border-radius: 6px; height: 32px; padding: 0 12px; font-size: 0.8rem; font-weight: 600; color: #4b5563; cursor: pointer; font-family: inherit; transition: border-color 0.15s, color 0.15s; display: inline-flex; align-items: center; box-sizing: border-box; }
.pagination-btn:hover:not(:disabled) { border-color: #1A6AFF; color: #1A6AFF; }
.pagination-btn:disabled { opacity: 0.45; cursor: not-allowed; }
.pagination-btn-go { background: #1A6AFF; border-color: #1A6AFF; color: #fff; }
.pagination-btn-go:hover:not(:disabled) { background: #1557e6; border-color: #1557e6; color: #fff; }
.pagination-jump { display: inline-flex; align-items: center; gap: 8px; margin-left: auto; }
.pagination-jump-lbl { white-space: nowrap; }
.pagination-input { width: 52px; height: 32px; border: 1px solid #e8eaf0; border-radius: 6px; padding: 0 8px; font-size: 14px; font-weight: 400; text-align: center; font-family: inherit; box-sizing: border-box; }
.pagination-input:focus { outline: none; border-color: #1A6AFF; box-shadow: 0 0 0 2px rgba(26, 106, 255, 0.15); }
@media (max-width: 720px) {
  .pagination-jump { margin-left: 0; width: 100%; }
}
.rpt-missing { min-height: 100vh; background: var(--bg-page, #f5f7fb); box-sizing: border-box; }
.rpt-missing-inner { max-width: 480px; margin: 40px auto 80px; padding: 32px 28px; text-align: center; background: #fff; border-radius: 14px; border: 1px solid #e8eaf0; box-shadow: 0 1px 4px rgba(60,72,120,.06); }
.rpt-missing-title { font-size: 1.05rem; font-weight: 700; color: #1a1d2e; margin: 0 0 12px; }
.rpt-missing-desc { font-size: 0.86rem; color: #6b7280; line-height: 1.65; margin: 0 0 22px; }
.rpt-missing .btn { margin: 6px; }

.rpt-sidebar { display: flex; flex-direction: column; gap: 0; min-height: 0; align-self: start; width: 100%; }
.meta-card { background: #fff; border: 1px solid #e8eaf0; border-radius: 14px; box-shadow: 0 1px 4px rgba(60,72,120,.06); overflow: hidden; }
.meta-card--metadata { min-height: 228px; display: flex; flex-direction: column; }
.meta-card--metadata .meta-card-body { flex: 1; }
.snapshot-card { margin-top: 14px; }
.meta-card-body { background: #fff; }
.meta-card-body .meta-row:last-child { border-bottom: none; }
.meta-card-hd { padding: 14px 20px; font-weight: 700; font-size: 0.9rem; background: #fafbff; border-bottom: 1px solid #f0f1f6; color: #1a1d2e; }
.meta-row { display: flex; justify-content: space-between; padding: 12px 20px; border-bottom: 1px solid #f4f5f9; font-size: 0.85rem; align-items: center; gap: 12px; }
.meta-lbl { color: #9ca3af; flex-shrink: 0; }
.meta-val { font-weight: 600; text-align: right; color: #4b5563; flex: 1; min-width: 0; }
.meta-link {
  color: #1A6AFF;
  font-weight: 600;
  text-decoration: none;
  border: none;
  background: none;
  cursor: pointer;
  padding: 0;
  font-size: inherit;
}
.meta-link:hover { text-decoration: underline; color: #2563eb; }
.meta-snapshot-block { padding: 14px 20px 18px; background: #fff; }
.snapshot-img { width: 100%; border: 1px solid #e8eaf0; border-radius: 8px; cursor: pointer; }
.snapshot-placeholder { padding: 24px 12px; text-align: center; background: #f9fafb; color: #9ca3af; font-size: 0.8rem; border-radius: 8px; border: 1px dashed #e8eaf0; }
.help-card { background: #1A6AFF; border-radius: 14px; padding: 20px 20px 22px; color: #fff; margin-top: 15px; box-sizing: border-box; display: flex; flex-direction: column; flex: 0 0 auto; }
.help-title { font-weight: 700; font-size: 0.95rem; margin: 0 0 10px; color: #fff; }
.help-desc { font-size: 0.8rem; opacity: .92; margin: 0 0 16px; line-height: 1.55; }
.help-btn-wrap { position: relative; display: inline-block; width: 100%; }
.help-btn { width: 100%; height: 36px; padding: 0; border-radius: 8px; background: rgba(255,255,255,.2); border: 1px solid rgba(255,255,255,.3); color: #fff; cursor: pointer; font-size: 0.85rem; font-weight: 600; display: flex; align-items: center; justify-content: center; box-sizing: border-box; }
.help-btn:hover { background: rgba(255,255,255,.3); }
.help-tooltip { position: absolute; bottom: 100%; left: 50%; transform: translateX(-50%); background: #1a1d2e; color: white; padding: 8px 12px; border-radius: 6px; font-size: 0.75rem; opacity: 0; visibility: hidden; transition: all 0.2s ease; white-space: nowrap; margin-bottom: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); pointer-events: none; z-index: 10; font-weight: 500; }
.help-tooltip::after { content: ''; position: absolute; top: 100%; left: 50%; transform: translateX(-50%); border-width: 5px; border-style: solid; border-color: #1a1d2e transparent transparent transparent; }
.help-btn-wrap:hover .help-tooltip { opacity: 1; visibility: visible; margin-bottom: 12px; }
.trend-card { display: flex; flex-direction: column; background: #fff; border: 1px solid #e8eaf0; border-radius: 14px; padding: 0 20px 22px; box-shadow: 0 1px 4px rgba(60,72,120,.06); margin-top: 15px; box-sizing: border-box; flex: 0 0 auto; }
.trend-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin: 0 -20px 12px;
  padding: 10px 20px;
  font-weight: 700;
  font-size: 0.9rem;
  background: #fafbff;
  border-bottom: 1px solid #f0f1f6;
  color: #1a1d2e;
}
.trend-title { font-size: 0.9rem; font-weight: 700; color: #1a1d2e; margin: 0; padding-bottom: 0; flex-shrink: 1; min-width: 0; }
.trend-filter-wrap {
  flex: 0 0 auto;
  width: 118px;
  min-width: 0;
}
.trend-filter-wrap :deep(.filter-select-trigger) {
  height: 32px;
  padding-top: 6px;
  padding-bottom: 6px;
  font-size: 12px;
  font-weight: 600;
  border-radius: 8px;
  border-color: #dbe0ea;
  color: #4b5563;
}
.trend-filter-wrap :deep(.filter-select-trigger:hover) {
  border-color: #c5cce0;
}
.trend-filter-wrap :deep(.filter-select-menu) {
  z-index: 400;
  min-width: 132px;
}
.trend-filter-wrap :deep(.filter-select-option) {
  font-size: 12px;
  padding: 8px 10px;
}
.trend-chart { display: flex; align-items: flex-end; justify-content: space-between; gap: 8px; margin-top: 10px; padding-top: 36px; box-sizing: border-box; border-top: 1px solid #f3f4f6; min-height: 0; }
.bar-wrap { flex: 0 0 auto; width: 26px; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; min-height: 0; }
.bar-column {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  min-height: 0;
  outline: none;
}
.bar-column:focus-visible {
  box-shadow: 0 0 0 2px rgba(26, 106, 255, 0.35);
  border-radius: 6px;
}
.trend-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-bottom: 8px;
  padding: 8px 10px;
  background: #1a1d2e;
  color: #fff;
  border-radius: 8px;
  line-height: 1.35;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  z-index: 20;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.2);
  text-align: center;
}
.bar-column:hover .trend-tooltip,
.bar-column:focus-visible .trend-tooltip {
  opacity: 1;
  visibility: visible;
}
.trend-tooltip-row {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 2px;
}
.trend-tooltip-num {
  font-size: 13px;
  font-weight: 800;
}
.trend-tooltip-unit {
  font-size: 10px;
  font-weight: 700;
  opacity: 0.92;
}
.trend-tooltip-date {
  margin-top: 5px;
  font-size: 10px;
  font-weight: 500;
  color: #cbd5e1;
}
.bar-fill { width: 14px; border-radius: 4px 4px 0 0; background: #dbeafe; transition: height 0.5s ease; min-height: 4px; }
.bar-fill.today { background: #1A6AFF; }
.trend-empty { font-size: 0.8rem; color: #9ca3af; text-align: center; padding: 16px 0 8px; margin-top: 8px; border-top: 1px solid #f3f4f6; }
.loading-state { padding: 100px; text-align: center; }
@media (max-width: 900px) {
  .rpt-head-row {
    flex-direction: column;
    align-items: flex-start;
  }
  .rpt-head-actions {
    width: 100%;
    flex-wrap: wrap;
  }
  .rpt-top-row { grid-template-columns: 1fr; }
  .rpt-left-stack { height: auto; }
  .distribution-card { flex: 0 1 auto; }
}
@media print {
  .no-print { display: none !important; }
  .rpt-body { background: white !important; }
  .rpt-page { padding-top: 0 !important; }
  .rpt-card { box-shadow: none !important; border: 1px solid #ddd !important; }
  /* 系统打印时尽量保留缩略图背景（整页截图为 background 时） */
  .real-thumb-crop { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
</style>

<style>
/* 导出弹窗（中文 UI，替代浏览器英文打印框） */
.export-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 20000;
  background: rgba(15, 23, 42, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  box-sizing: border-box;
}
.export-modal {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: 14px;
  padding: 22px 24px 20px;
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.2);
  box-sizing: border-box;
}
.export-modal-title {
  margin: 0 0 10px 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #1a1d2e;
}
.export-modal-hint {
  margin: 0 0 16px 0;
  font-size: 0.85rem;
  color: #6b7280;
  line-height: 1.55;
}
.export-modal-label {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  color: #4b5563;
  margin-bottom: 6px;
}
.export-modal-select {
  width: 100%;
  height: 40px;
  padding: 0 12px;
  border: 1px solid #e2e4ec;
  border-radius: 8px;
  font-size: 14px;
  color: #1a1d2e;
  background: #fff;
  box-sizing: border-box;
  margin-bottom: 18px;
}
.export-modal-progress-wrap {
  margin: 2px 0 14px;
}
.export-modal-progress-text {
  font-size: 12px;
  color: #4b5563;
  margin-bottom: 6px;
}
.export-modal-progress-track {
  position: relative;
  height: 8px;
  border-radius: 999px;
  background: #e5e7eb;
  overflow: hidden;
}
.export-modal-progress-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #1a6aff, #4f6fff);
  transition: width 0.22s ease;
}
.export-modal-progress-percent {
  margin-top: 6px;
  text-align: right;
  font-size: 12px;
  color: #6b7280;
}
.export-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
.export-modal-btn {
  height: 38px;
  padding: 0 18px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  box-sizing: border-box;
}
.export-modal-btn--ghost {
  background: #f3f4f6;
  color: #4b5563;
}
.export-modal-btn--primary {
  background: #1a6aff;
  color: #fff;
}
.export-modal-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
/* 离屏导出画布（html2canvas） */
.report-export-panel {
  position: fixed;
  left: -12000px;
  top: 0;
  width: 794px;
  padding: 0;
  background: transparent;
  color: #1a1d2e;
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 13px;
  line-height: 1.6;
  box-sizing: border-box;
  z-index: 0;
  pointer-events: none;
}
.rep-ex-page {
  width: 794px;
  min-height: 1123px;
  padding: 28px 32px 34px;
  box-sizing: border-box;
  background: #fff;
  overflow: hidden;
}
.rep-ex-page + .rep-ex-page {
  margin-top: 20px;
}
.rep-ex-top-cards {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.report-export-panel .chart-item {
  gap: 4px;
}
.rep-ex-h1 {
  margin: 0 0 16px 0;
  font-size: 22px;
  font-weight: 800;
  color: #1a1d2e;
}
.rep-ex-line {
  margin: 0 0 8px 0;
  word-break: break-all;
}
.rep-ex-block {
  margin: 16px 0;
  padding: 12px 0;
  border-top: 1px solid #e8eaf0;
}
.rep-ex-subhd {
  font-weight: 700;
  margin-bottom: 8px;
  color: #1a1d2e;
  font-size: 18px;
}
.rep-ex-snapshot-wrap {
  margin-top: 10px;
  border: 1px solid #e8eaf0;
  border-radius: 12px;
  padding: 10px;
}
.rep-ex-full-img--page {
  width: 100%;
  max-height: 980px;
  object-fit: contain;
}
.rep-ex-diag-list {
  margin: 0;
  padding-left: 18px;
}
.rep-ex-diag-list li {
  margin-bottom: 6px;
}
.rep-ex-diag :deep(strong) {
  font-weight: 700;
  color: #1a1d2e;
}
.rep-ex-full-img {
  display: block;
  max-width: 100%;
  height: auto;
  border: 1px solid #e8eaf0;
  border-radius: 8px;
  margin-top: 8px;
}
.rep-ex-table {
  width: 100%;
  table-layout: fixed;
  border-collapse: collapse;
  border: 1px solid #e5e7eb;
  margin-top: 10px;
}
.rep-ex-table th,
.rep-ex-table td {
  border: 1px solid #e5e7eb;
  padding: 8px;
  vertical-align: top;
  font-size: 12px;
  color: #374151;
  word-break: break-word;
}
.rep-ex-table th {
  background: #f8fafc;
  color: #111827;
  font-weight: 700;
}
.rep-ex-table .col-index { width: 56px; }
.rep-ex-table .col-thumb { width: 170px; }
.rep-ex-table .col-title { width: 140px; }
.rep-ex-table .col-desc { width: 210px; }
.rep-ex-table .col-sug { width: auto; }
.rep-ex-td-center {
  text-align: center;
}
.rep-ex-table tr {
  break-inside: avoid;
  page-break-inside: avoid;
}
.rep-ex-thumb {
  display: block;
  width: 180px;
  max-width: 100%;
  height: auto;
  border: 1px solid #e8eaf0;
  border-radius: 6px;
  break-inside: avoid;
  page-break-inside: avoid;
}
.rep-ex-thumb-empty {
  color: #9ca3af;
  font-size: 12px;
}
</style>
