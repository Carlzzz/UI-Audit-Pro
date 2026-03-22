<template>
  <div class="page-container">
    <AppNavbar variant="full" active-key="config" />
    <SpecAddFloat
      v-model:open="specFloat.open"
      :left="specFloat.left"
      :top="specFloat.top"
      :title="specFloat.title"
      :field-label="specFloat.fieldLabel"
      :default-val="specFloat.defaultVal"
      :mode="specFloat.mode"
      @confirm="onSpecFloatConfirm"
    />
    <SpecColorFloat
      v-model:open="colorFloat.open"
      :left="colorFloat.left"
      :top="colorFloat.top"
      :title="colorFloat.title"
      :initial-label="colorFloat.label"
      :initial-hex="colorFloat.hex"
      @confirm="onColorFloatConfirm"
    />
    <div class="config-layout">
      <!-- 左侧边栏 -->
      <div class="sidebar" >
        <div class="sidebar-title">规范管理</div>
        <div class="nav-item" :class="{active: activeTab === 'baseline'}" @click="activeTab = 'baseline'">
           <span class="icon" aria-hidden="true"><IconStroke name="baseline" size="sm" /></span> 基准值模式
        </div>
        <div class="nav-group">
          <div class="nav-item group-title" :class="{active: activeTab.startsWith('comp_')}" @click="toggleComponentMenu">
            <span class="icon" aria-hidden="true"><IconStroke name="component" size="sm" /></span> 组件模式
            <span class="arrow" aria-hidden="true"><IconStroke name="chevron-down" size="sm" class="nav-chevron" :class="{ open: expandComponents }" /></span>
          </div>
          <div class="sub-nav" v-show="expandComponents">
            <div class="sub-item" :class="{active: activeTab === 'comp_global'}" @click.stop="activeTab = 'comp_global'">全局基础规范</div>
            <div class="sub-item" :class="{active: activeTab === 'comp_btn'}" @click.stop="activeTab = 'comp_btn'">按钮组件</div>
            <div class="sub-item" :class="{active: activeTab === 'comp_input'}" @click.stop="activeTab = 'comp_input'">数据录入类组件</div>
            <div class="sub-item" :class="{active: activeTab === 'comp_nav'}" @click.stop="activeTab = 'comp_nav'">数据展示与导航组件</div>
          </div>
        </div>
        <div class="nav-item" :class="{active: activeTab === 'design'}" @click="activeTab = 'design'">
           <span class="icon" aria-hidden="true"><IconStroke name="design" size="sm" /></span> 设计稿模式
        </div>
      </div>

      <!-- 右侧主体区 -->
      <div class="main-content">
        <div class="config-panel-sheet">
        <div class="content-header">
          <div class="content-header-inner">
            <div class="breadcrumb">规范管理 <span class="sep">/</span> <span class="cur">{{ headerTitle }}</span></div>
            <div class="content-header-title-row">
              <h2 class="content-header-h2">{{ headerTitle }}</h2>
              <div class="toggle-group-top" @click.stop="toggleGlobalEnable">
                <span class="toggle-group-top-label">一键开启</span>
                <div class="toggle" :class="{on: currentGlobalEnable}"></div>
              </div>
            </div>
            <p class="subtitle">定义设计走查的全局基准规范或接入设计资源</p>
          </div>
        </div>

        <div v-if="activeTab === 'baseline'" class="form-container">
          <!-- 1. 视觉一致性标准 -->
          <div class="section-title">
            <span class="section-icon" aria-hidden="true"><IconStroke name="palette" size="md" /></span>
            1. 视觉一致性标准
          </div>
          <div class="grid-2 align-start">
            <div class="col-left">
              <!-- 全局色盘 -->
              <div class="card mb-4">
                <h4>全局色盘</h4>
                <div class="color-list">
                  <div class="color-row" v-for="(color, idx) in baselineConfig.colors" :key="idx" @click.stop="editColor($event, idx)" style="cursor:pointer;">
                    <div class="color-box" :style="{background: color.hex}"></div>
                    <div class="color-name">{{color.label}}</div>
                    <div class="color-hex">{{color.hex}}</div>
                    <button class="btn-del" @click.stop="baselineConfig.colors.splice(idx, 1)">🗑</button>
                  </div>
                  <div class="btn-add" @click.stop="addColor($event)">+ 添加色值</div>
                  <div class="form-row mt-3">
                    <label>偏差阈值：</label>
                    <input type="text" v-model="baselineConfig.colorThreshold" class="input-sm" style="width:80px; padding:4px; border:1px solid #e2e4ec; border-radius:4px;" />
                  </div>
                </div>
              </div>

              <!-- 栅格与圆角 -->
              <div class="card mb-4">
                <h4>栅格与圆角</h4>
                <div class="form-row mt-2" @click="baselineConfig.gridCheck = !baselineConfig.gridCheck">
                  <label>栅格对齐检测（px 倍数）</label>
                  <div class="toggle" :class="{on: baselineConfig.gridCheck}"></div>
                </div>
                <p class="field-hint">填写栅格基准 px（如 8、4）。走查时宽度及容器 margin/padding 须为<strong>其中任一数的整数倍</strong>，满足一条即通过；可自由增删改。</p>
                <div class="tags mt-2">
                  <span class="tag" v-for="(t, idx) in baselineConfig.gridTokens" :key="'g'+idx">{{t}} <span class="tag-rm" @click="removeToken(baselineConfig.gridTokens, idx)">🗑</span></span>
                  <span class="tag-add" @click="addToken($event, baselineConfig.gridTokens, '8px', '添加栅格基准值')">+ 添加</span>
                </div>
                
                <div class="form-row mt-4" @click="baselineConfig.radiusCheck = !baselineConfig.radiusCheck">
                  <label>圆角规范</label>
                  <div class="toggle" :class="{on: baselineConfig.radiusCheck}"></div>
                </div>
                <div class="tags mt-2">
                  <span class="tag" v-for="(t, idx) in baselineConfig.radiusTokens" :key="'r'+idx">{{t}} <span class="tag-rm" @click="removeToken(baselineConfig.radiusTokens, idx)">🗑</span></span>
                  <span class="tag-add" @click="addToken($event, baselineConfig.radiusTokens, '16px', '添加圆角值')">+ 添加</span>
                </div>
              </div>

              <!-- 动画与过渡 -->
              <div class="card mb-4">
                <h4>动画与过渡</h4>
                <div class="form-row mt-2" @click="baselineConfig.transitionCheck = !baselineConfig.transitionCheck">
                  <label>过渡持续时间</label>
                  <div class="toggle" :class="{on: baselineConfig.transitionCheck}"></div>
                </div>
                <div class="form-group mt-2">
                   <input type="text" v-model="baselineConfig.transitions" @blur="normBaselineListFields" />
                </div>
              </div>

              <!-- 按钮与输入框 -->
              <div class="card mb-4">
                <h4>按钮与输入框</h4>
                <p class="field-hint">本区块在规范页中的排版顺序参考左侧「栅格与圆角」；高度走查与栅格倍数无关。</p>
                <div class="form-group mt-2">
                  <div
                    class="form-row"
                    role="switch"
                    :aria-checked="baselineConfig.buttonHeightCheck"
                    @click="baselineConfig.buttonHeightCheck = !baselineConfig.buttonHeightCheck"
                  >
                    <label>按钮高度（px，须与实测一致）</label>
                    <div class="toggle" :class="{on: baselineConfig.buttonHeightCheck}" aria-hidden="true"></div>
                  </div>
                  <div class="tags mt-2">
                    <span class="tag" v-for="(t, idx) in baselineConfig.buttonHeightTokens" :key="'bh'+idx">{{t}} <span class="tag-rm" @click="removeToken(baselineConfig.buttonHeightTokens, idx)">✕</span></span>
                    <span class="tag-add" @click="addToken($event, baselineConfig.buttonHeightTokens, '32px', '添加按钮高度规范值')">+ 添加</span>
                  </div>
                </div>
                <div class="form-group mt-2">
                  <div
                    class="form-row"
                    role="switch"
                    :aria-checked="baselineConfig.inputSelectHeightCheck"
                    @click="baselineConfig.inputSelectHeightCheck = !baselineConfig.inputSelectHeightCheck"
                  >
                    <label>输入框/选择器高度（px，须与实测一致）</label>
                    <div class="toggle" :class="{on: baselineConfig.inputSelectHeightCheck}" aria-hidden="true"></div>
                  </div>
                  <div class="tags mt-2">
                    <span class="tag" v-for="(t, idx) in baselineConfig.inputHeightTokens" :key="'ih'+idx">{{t}} <span class="tag-rm" @click="removeToken(baselineConfig.inputHeightTokens, idx)">✕</span></span>
                    <span class="tag-add" @click="addToken($event, baselineConfig.inputHeightTokens, '32px', '添加输入框/选择器高度规范值')">+ 添加</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="col-right">
              <!-- 字体与排版 -->
              <div class="card mb-4">
                <h4>字体与排版</h4>
                <div class="form-group">
                  <label>字体族</label>
                  <input type="text" v-model="baselineConfig.fontFamily" @blur="normBaselineListFields" />
                </div>
                <div class="form-group">
                  <label>字体大小</label>
                  <input type="text" v-model="baselineConfig.fontSizes" @blur="normBaselineListFields" />
                </div>
                <div class="form-group">
                  <label>行高</label>
                  <input type="text" v-model="baselineConfig.lineHeights" @blur="normBaselineListFields" />
                </div>
                <div class="form-group">
                  <label>字重</label>
                  <input type="text" v-model="baselineConfig.fontWeights" @blur="normBaselineListFields" />
                </div>
                <div class="form-group">
                  <label>间距规范（px 倍数）</label>
                  <p class="field-hint">填写间距基准 px（如 4、8）。走查时 margin/padding 须为<strong>其中任一数的整数倍</strong>，满足一条即通过；可自由增删改。</p>
                  <div class="tags">
                    <span class="tag" v-for="(t, idx) in baselineConfig.spacingTokens" :key="'s'+idx">{{t}} <span class="tag-rm" @click="removeToken(baselineConfig.spacingTokens, idx)">✕</span></span>
                    <span class="tag-add" @click="addToken($event, baselineConfig.spacingTokens, '8px', '添加间距基准值')">+ 添加</span>
                  </div>
                </div>
              </div>

              <!-- 阴影与图标 -->
              <div class="card mb-4">
                <h4>阴影与图标</h4>
                <div class="form-row mt-2" @click="baselineConfig.shadowCheck = !baselineConfig.shadowCheck">
                  <label>投影规范</label>
                  <div class="toggle" :class="{on: baselineConfig.shadowCheck}"></div>
                </div>
                <div class="form-group mt-2">
                   <select v-model="baselineConfig.shadowPreset">
                     <option>符合 Ant Design 投影规范</option>
                     <option>符合 Material Design 投影规范</option>
                   </select>
                </div>

                <div class="form-row mt-4" @click="baselineConfig.iconCheck = !baselineConfig.iconCheck">
                  <label>图标规范</label>
                  <div class="toggle" :class="{on: baselineConfig.iconCheck}"></div>
                </div>
                <div class="tags mt-2">
                  <span class="tag" v-for="(t, idx) in baselineConfig.iconTokens" :key="'i'+idx">{{t}} <span class="tag-rm" @click="removeToken(baselineConfig.iconTokens, idx)">🗑</span></span>
                  <span class="tag-add" @click="addToken($event, baselineConfig.iconTokens, '24*24px', '添加图标尺寸')">+ 添加</span>
                </div>

                <div class="form-row mt-4" @click="baselineConfig.iconStyleCheck = !baselineConfig.iconStyleCheck">
                  <label>图标风格一致性 (描边/填充)</label>
                  <div class="toggle" :class="{on: baselineConfig.iconStyleCheck}"></div>
                </div>

                <div class="form-group mt-3">
                  <label>图标描边粗细</label>
                  <div class="tags">
                    <span class="tag" v-for="(t, idx) in baselineConfig.iconStrokeTokens" :key="'is'+idx">{{t}} <span class="tag-rm" @click="removeToken(baselineConfig.iconStrokeTokens, idx)">🗑</span></span>
                    <span class="tag-add" @click="addToken($event, baselineConfig.iconStrokeTokens, '2.5px', '添加描边粗细')">+ 添加</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 2. 交互与布局标准 -->
          <div class="section-title mt-4">
            <span class="section-icon" aria-hidden="true"><IconStroke name="cursor" size="md" /></span>
            2. 交互与布局标准
          </div>
          <div class="grid-3">
            <div class="card">
              <h5 class="mb-3 text-bold">交互与操作反馈</h5>
              <div class="form-group">
                <label>最小点击热区</label>
                <div class="input-with-unit"><input type="number" v-model="baselineConfig.minClickArea" /><span>px</span></div>
              </div>
              <div class="form-row mt-3" @click="baselineConfig.hoverCheck = !baselineConfig.hoverCheck">
                <label>组件触发状态<br/><small>检测 Hover/Active/Focus/Disable</small></label>
                <div class="toggle" :class="{on: baselineConfig.hoverCheck}"></div>
              </div>
              <div class="form-row mt-3" @click="baselineConfig.gestureCheck = !baselineConfig.gestureCheck">
                <label>鼠标手势<br/><small>可点击小手，禁用圆圈+斜杠</small></label>
                <div class="toggle" :class="{on: baselineConfig.gestureCheck}"></div>
              </div>
            </div>
            <div class="card">
              <h5 class="mb-3 text-bold">布局与边界控制</h5>
              <div class="form-group">
                <label>文本溢出</label>
                <FilterSelect
                  v-model="baselineConfig.textOverflow"
                  :options="textOverflowOptions"
                  menu-label="文本溢出"
                />
              </div>
              <div class="form-row mt-3" @click="baselineConfig.responsiveCheck = !baselineConfig.responsiveCheck">
                <label>响应式适配<br/><small>走查时校验常用布局断点宽度（px）</small></label>
                <div class="toggle" :class="{on: baselineConfig.responsiveCheck}"></div>
              </div>
              <div class="tags mt-2">
                <span class="tag" v-for="(t, idx) in baselineConfig.responsiveBreakpoints" :key="'resp'+idx">{{ t }} <span class="tag-rm" @click.stop="removeToken(baselineConfig.responsiveBreakpoints, idx)">🗑</span></span>
                <span class="tag-add" @click.stop="addToken($event, baselineConfig.responsiveBreakpoints, '768px', '添加响应式断点')">+ 添加</span>
              </div>
              <div class="form-row mt-3" @click="baselineConfig.zIndexCheck = !baselineConfig.zIndexCheck">
                <label>层级与遮挡<br/><small>确保弹窗等处于最高层级不被遮挡</small></label>
                <div class="toggle" :class="{on: baselineConfig.zIndexCheck}"></div>
              </div>
            </div>
            <div class="card">
              <h5 class="mb-3 text-bold">场景与状态兜底</h5>
               <div class="form-row mt-3" @click="baselineConfig.emptyStateCheck = !baselineConfig.emptyStateCheck">
                <label>空状态覆盖<br/><small>列表无数据时是否配置占位图</small></label>
                <div class="toggle" :class="{on: baselineConfig.emptyStateCheck}"></div>
              </div>
              <div class="form-row mt-3" @click="baselineConfig.loadingStateCheck = !baselineConfig.loadingStateCheck">
                <label>加载状态预设<br/><small>异步请求关联 SKELETON 或 SPINNER</small></label>
                <div class="toggle" :class="{on: baselineConfig.loadingStateCheck}"></div>
              </div>
            </div>
          </div>

          <!-- 3. 无障碍与合规性 -->
          <div class="section-title mt-4">
            <span class="section-icon" aria-hidden="true"><IconStroke name="accessibility" size="md" /></span>
            3. 无障碍与合规性
          </div>
          <div class="grid-4">
             <div class="card a11y-card">
                <h5>色彩对比度阈值</h5>
                <div class="contrast-row">
                  <span class="text-blue contrast-ratio">≤ 4.5:1</span>
                  <span class="badge">AA级标准</span>
                </div>
                <p class="desc a11y-desc">正文与背景对比度须满足 WCAG AA 级要求。</p>
                <div class="a11y-footer">
                  <div class="toggle" :class="{on: baselineConfig.contrastCheck}" @click="baselineConfig.contrastCheck = !baselineConfig.contrastCheck"></div>
                </div>
             </div>
             <div class="card a11y-card">
                <h5>图片 Alt 属性</h5>
                <p class="desc a11y-desc">强制检测 IMG 标签是否包含替代文本(ALT TEXT)</p>
                <div class="a11y-footer">
                  <div class="toggle" :class="{on: baselineConfig.altCheck}" @click="baselineConfig.altCheck = !baselineConfig.altCheck"></div>
                </div>
             </div>
             <div class="card a11y-card">
                <h5>DOM 语义化</h5>
                <p class="desc a11y-desc">检测 H1-H6 层级顺序是否严密，是否跨级</p>
                <div class="a11y-footer">
                  <div class="toggle" :class="{on: baselineConfig.domSemantics}" @click="baselineConfig.domSemantics = !baselineConfig.domSemantics"></div>
                </div>
             </div>
             <div class="card a11y-card">
                <h5>焦点顺序逻辑</h5>
                <p class="desc a11y-desc">检测 TAB 键切换时焦点流转是否符合从左到右</p>
                <div class="a11y-footer">
                  <div class="toggle" :class="{on: baselineConfig.focusOrder}" @click="baselineConfig.focusOrder = !baselineConfig.focusOrder"></div>
                </div>
             </div>
          </div>

          <!-- 4. 性能与内容质量 -->
          <div class="section-title mt-4">
            <span class="section-icon" aria-hidden="true"><IconStroke name="bolt" size="md" /></span>
            4. 性能与内容质量
          </div>
          <div class="grid-2">
             <div class="card">
               <div class="form-group">
                 <label>图片资源限制</label>
                 <div class="input-with-unit"><input type="number" v-model="baselineConfig.imageSizeLimit" /><span>KB</span></div>
               </div>
               <div class="form-row mt-3" @click="baselineConfig.hardcodeCheck = !baselineConfig.hardcodeCheck">
                 <label>硬编码检测<br/><small>前端代码内直接写死的中文汉字</small></label>
                 <div class="toggle" :class="{on: baselineConfig.hardcodeCheck}"></div>
               </div>
             </div>
             <div class="card">
               <div class="form-row mt-3" @click="baselineConfig.deadlinkCheck = !baselineConfig.deadlinkCheck">
                 <label>死链扫描<br/><small>HTTP状态巡检，检测是否存在 404 死链</small></label>
                 <div class="toggle" :class="{on: baselineConfig.deadlinkCheck}"></div>
               </div>
               <div class="form-row mt-3" @click="baselineConfig.textFormatCheck = !baselineConfig.textFormatCheck">
                 <label>数据与文案<br/><small>中英文空格，日期格式统一为 YYYY-MM-DD</small></label>
                 <div class="toggle" :class="{on: baselineConfig.textFormatCheck}"></div>
               </div>
             </div>
          </div>
        </div>

        <!-- ====== 全局基础规范 ====== -->
        <div v-if="activeTab === 'comp_global'" class="form-container">
          <p class="comp-desc">本规范基于 Global Foundation 的核心规范框架，旨在为设计师与开发者提供高度统一一致、历经反复专业内构建规范。</p>

          <!-- 1. 品牌色 -->
          <div class="section-title"><span class="section-num">◈ 1.</span> 品牌色</div>
          <div class="grid-6 mb-4">
            <div v-for="(c, idx) in componentConfig.brandColors" :key="'bc'+idx" class="color-card">
              <div class="color-block" :style="{background: c.hex}"></div>
              <div class="color-info">
                <strong>{{ c.label }}</strong>
                <div class="hex">{{ c.hex }}</div>
                <div class="color-desc">{{ c.desc }}</div>
              </div>
            </div>
          </div>

          <!-- 2. 中性色 -->
          <div class="section-title"><span class="section-num">◈ 2.</span> 中性色</div>
          <div class="grid-3 mb-4">
            <div v-for="(c, idx) in componentConfig.neutralColors" :key="'nc'+idx" class="color-row-item">
              <div class="color-box" :style="{background: c.hex}"></div>
              <div>
                <div style="font-size:13px; font-weight:600; color:#1a1d2e;">{{ c.label }}</div>
                <div style="font-size:12px; color:#6b7280; font-family:monospace;">{{ c.hex }}</div>
              </div>
            </div>
          </div>

          <!-- 3. 文字色 -->
          <div class="section-title"><span class="section-num">◈ 3.</span> 文字色</div>
          <div class="grid-2 mb-4 align-start">
            <div class="card">
              <h5 class="mb-3 text-bold">主文字色</h5>
              <div class="text-color-row" v-for="(val, key) in componentConfig.textColors" :key="'tc'+key">
                <div class="color-box-sm" :style="{background: val}"></div>
                <span class="tc-key">{{ key }}</span>
                <span class="tc-val">{{ val }}</span>
              </div>
            </div>
            <div class="card">
              <h5 class="mb-3 text-bold">排版规范</h5>
              <div class="form-group">
                <label>字体族</label>
                <input type="text" v-model="componentConfig.typography.family" />
              </div>
              <div class="form-group">
                <label>字体大小</label>
                <input type="text" v-model="componentConfig.typography.sizes" />
              </div>
              <div class="form-group">
                <label>行高</label>
                <input type="text" v-model="componentConfig.typography.lineHeights" />
              </div>
              <div class="form-group">
                <label>字重</label>
                <input type="text" v-model="componentConfig.typography.weights" />
              </div>
            </div>
          </div>

          <!-- 5. 间距与栅格 -->
          <div class="section-title"><span class="section-num">◈ 5.</span> 间距与栅格</div>
          <div class="grid-2 mb-4 align-start">
            <div class="card">
              <h5 class="mb-3 text-bold">基础间距</h5>
              <div class="spacing-row" v-for="(s, idx) in componentConfig.spacing" :key="'sp'+idx">
                <span class="spacing-label">{{ s }}</span>
                <div class="spacing-bar" :style="{width: parseInt(s)*3+'px'}"></div>
                <span class="spacing-name">基础间距 {{ idx+1 }}</span>
              </div>
              <div class="btn-add mt-3" @click="addArrayItem($event, componentConfig.spacing, '20px')">+ 添加间距</div>
            </div>
            <div class="card">
              <h5 class="mb-3 text-bold">栅格系统</h5>
              <div class="form-group">
                <label>栅格基准值 (px)</label>
                <div class="tags">
                  <span class="tag" v-for="(g, idx) in componentConfig.grid" :key="'g'+idx">{{ g }} <span class="tag-rm" @click="componentConfig.grid.splice(idx,1)">✕</span></span>
                  <span class="tag-add" @click="addArrayItem($event, componentConfig.grid, '8px')">+ 添加</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 6. 圆角规范 -->
          <div class="section-title"><span class="section-num">◈ 6.</span> 圆角规范</div>
          <div class="grid-2 mb-4 align-start">
            <div class="card">
              <h5 class="mb-3 text-bold">字体与排版</h5>
              <div class="form-group">
                <label>字体族</label>
                <input type="text" v-model="componentConfig.typography.family" />
              </div>
              <div class="form-row mt-2">
                <label>图标规范</label>
                <div class="toggle" :class="{on: true}"></div>
              </div>
              <div class="tags mt-2">
                <span class="tag" v-for="(s, idx) in componentConfig.icons.sizes" :key="'is'+idx">{{ s }} <span class="tag-rm" @click="componentConfig.icons.sizes.splice(idx,1)">✕</span></span>
                <span class="tag-add" @click="addArrayItem($event, componentConfig.icons.sizes, '20*20px')">+ 添加</span>
              </div>
              <div class="form-row mt-3">
                <label>图标描边粗细</label>
                <div class="toggle" :class="{on: true}"></div>
              </div>
              <div class="tags mt-2">
                <span class="tag" v-for="(s, idx) in componentConfig.icons.strokes" :key="'st'+idx">{{ s }} <span class="tag-rm" @click="componentConfig.icons.strokes.splice(idx,1)">✕</span></span>
                <span class="tag-add" @click="addArrayItem($event, componentConfig.icons.strokes, '2px')">+ 添加</span>
              </div>
            </div>
            <div class="card">
              <h5 class="mb-3 text-bold">圆角系统</h5>
              <div class="tags">
                <span class="tag" v-for="(r, idx) in componentConfig.icons.radius" :key="'r'+idx">{{ r }} <span class="tag-rm" @click="componentConfig.icons.radius.splice(idx,1)">✕</span></span>
                <span class="tag-add" @click="addArrayItem($event, componentConfig.icons.radius, '16px')">+ 添加</span>
              </div>
              <div class="form-row mt-3">
                <label>投影预设</label>
              </div>
              <select v-model="componentConfig.shadowPreset" class="mt-2" style="width:100%;padding:10px;border:1px solid #e2e4ec;border-radius:6px;">
                <option>符合 Ant Design 投影规范</option>
                <option>符合 Material Design 投影规范</option>
              </select>
            </div>
          </div>
        </div>

        <!-- ====== 按钮组件 ====== -->
        <div v-if="activeTab === 'comp_btn'" class="form-container">
          <p class="comp-desc">本规范基于 Global Foundation 的核心规范框架，旨在为设计师与开发者提供高度统一一致、历经反复专业内构建规范。</p>

          <!-- 1. 主按钮 -->
          <div class="section-title"><span class="section-num">◈ 1.</span> 主按钮</div>
          <div class="card mb-4">
            <div class="grid-2 align-start">
              <div>
                <h5 class="mb-3">状态规范</h5>
                <div class="btn-states">
                  <button class="demo-btn primary">默认</button>
                  <button class="demo-btn primary hover">悬浮</button>
                  <button class="demo-btn primary active">点击</button>
                  <button class="demo-btn primary disabled" disabled>不可用</button>
                </div>
                <div class="btn-state-values mt-2">
                  <div class="bsv">
                    <div class="bsv-dot" style="background:#1A6AFF"></div>
                    <span>常规 #1A6AFF</span>
                  </div>
                  <div class="bsv">
                    <div class="bsv-dot" style="background:#256AF4"></div>
                    <span>悬浮 #256AF4</span>
                  </div>
                  <div class="bsv">
                    <div class="bsv-dot" style="background:#145BD7"></div>
                    <span>点击 #145BD7</span>
                  </div>
                  <div class="bsv">
                    <div class="bsv-dot" style="background:#A3C3FF"></div>
                    <span>禁用 #A3C3FF</span>
                  </div>
                </div>
              </div>
              <div>
                <h5 class="mb-3">尺寸与间距</h5>
                <div class="form-group">
                  <label>高度</label>
                  <div class="tags">
                    <span class="tag" v-for="(h,i) in componentConfig.buttons.primary.height" :key="'ph'+i">{{ h }} <span class="tag-rm" @click="componentConfig.buttons.primary.height.splice(i,1)">✕</span></span>
                    <span class="tag-add" @click="addArrayItem($event, componentConfig.buttons.primary.height,'40px')">+ 添加</span>
                  </div>
                </div>
                <div class="form-group">
                  <label>圆角</label>
                  <div class="tags">
                    <span class="tag" v-for="(r,i) in componentConfig.buttons.primary.radius" :key="'pr'+i">{{ r }} <span class="tag-rm" @click="componentConfig.buttons.primary.radius.splice(i,1)">✕</span></span>
                    <span class="tag-add" @click="addArrayItem($event, componentConfig.buttons.primary.radius,'6px')">+ 添加</span>
                  </div>
                </div>
                <div class="form-group">
                  <label>文字大小 (Padding)</label>
                  <div class="tags">
                    <span class="tag" v-for="(p,i) in componentConfig.buttons.primary.padding" :key="'pp'+i">{{ p }} <span class="tag-rm" @click="componentConfig.buttons.primary.padding.splice(i,1)">✕</span></span>
                    <span class="tag-add" @click="addArrayItem($event, componentConfig.buttons.primary.padding,'24px')">+ 添加</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 2. 次按钮 -->
          <div class="section-title"><span class="section-num">◈ 2.</span> 次按钮</div>
          <div class="card mb-4">
            <div class="grid-2 align-start">
              <div>
                <h5 class="mb-3">状态规范</h5>
                <div class="btn-states">
                  <button class="demo-btn secondary">默认</button>
                  <button class="demo-btn secondary hover">悬浮</button>
                  <button class="demo-btn secondary active-s">点击</button>
                  <button class="demo-btn secondary disabled" disabled>不可用</button>
                </div>
                <div class="btn-state-values mt-2">
                  <div class="bsv"><div class="bsv-dot" style="background:#F0F4FF"></div><span>常规 #F0F4FF</span></div>
                  <div class="bsv"><div class="bsv-dot" style="background:#EAF0FF"></div><span>悬浮 #EAF0FF</span></div>
                  <div class="bsv"><div class="bsv-dot" style="background:#EFF1F7"></div><span>点击 #EFF1F7</span></div>
                  <div class="bsv"><div class="bsv-dot" style="background:#F5F7FA"></div><span>禁用 #F5F7FA</span></div>
                </div>
              </div>
              <div>
                <h5 class="mb-3">尺寸与间距</h5>
                <div class="form-group">
                  <label>高度</label>
                  <div class="tags">
                    <span class="tag" v-for="(h,i) in componentConfig.buttons.secondary.height" :key="'sh'+i">{{ h }} <span class="tag-rm" @click="componentConfig.buttons.secondary.height.splice(i,1)">✕</span></span>
                    <span class="tag-add" @click="addArrayItem($event, componentConfig.buttons.secondary.height,'40px')">+ 添加</span>
                  </div>
                </div>
                <div class="form-group">
                  <label>圆角</label>
                  <div class="tags">
                    <span class="tag" v-for="(r,i) in componentConfig.buttons.secondary.radius" :key="'sr'+i">{{ r }} <span class="tag-rm" @click="componentConfig.buttons.secondary.radius.splice(i,1)">✕</span></span>
                    <span class="tag-add" @click="addArrayItem($event, componentConfig.buttons.secondary.radius,'6px')">+ 添加</span>
                  </div>
                </div>
                <div class="form-group">
                  <label>文字大小 (Padding)</label>
                  <div class="tags">
                    <span class="tag" v-for="(p,i) in componentConfig.buttons.secondary.padding" :key="'sp2'+i">{{ p }} <span class="tag-rm" @click="componentConfig.buttons.secondary.padding.splice(i,1)">✕</span></span>
                    <span class="tag-add" @click="addArrayItem($event, componentConfig.buttons.secondary.padding,'24px')">+ 添加</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 3. 虚线按钮 -->
          <div class="section-title"><span class="section-num">◈ 3.</span> 虚线按钮</div>
          <div class="card mb-4">
            <div class="grid-2 align-start">
              <div>
                <h5 class="mb-3">状态规范</h5>
                <div class="btn-states">
                  <button class="demo-btn dashed">默认</button>
                  <button class="demo-btn dashed">悬浮</button>
                  <button class="demo-btn dashed">点击</button>
                  <button class="demo-btn dashed disabled" disabled>不可用</button>
                </div>
              </div>
              <div>
                <h5 class="mb-3">尺寸与间距</h5>
                <div class="form-group">
                  <label>高度</label>
                  <div class="tags">
                    <span class="tag" v-for="(h,i) in componentConfig.buttons.dashed.height" :key="'dh'+i">{{ h }} <span class="tag-rm" @click="componentConfig.buttons.dashed.height.splice(i,1)">✕</span></span>
                    <span class="tag-add" @click="addArrayItem($event, componentConfig.buttons.dashed.height,'40px')">+ 添加</span>
                  </div>
                </div>
                <div class="form-group">
                  <label>圆角</label>
                  <div class="tags">
                    <span class="tag" v-for="(r,i) in componentConfig.buttons.dashed.radius" :key="'dr'+i">{{ r }} <span class="tag-rm" @click="componentConfig.buttons.dashed.radius.splice(i,1)">✕</span></span>
                    <span class="tag-add" @click="addArrayItem($event, componentConfig.buttons.dashed.radius,'6px')">+ 添加</span>
                  </div>
                </div>
                <div class="form-group">
                  <label>文字大小 (Padding)</label>
                  <div class="tags">
                    <span class="tag" v-for="(p,i) in componentConfig.buttons.dashed.padding" :key="'dp'+i">{{ p }} <span class="tag-rm" @click="componentConfig.buttons.dashed.padding.splice(i,1)">✕</span></span>
                    <span class="tag-add" @click="addArrayItem($event, componentConfig.buttons.dashed.padding,'24px')">+ 添加</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 4. 文字按钮 -->
          <div class="section-title"><span class="section-num">◈ 4.</span> 文字按钮</div>
          <div class="card mb-4">
            <div class="grid-2 align-start">
              <div>
                <h5 class="mb-3">状态规范</h5>
                <div class="btn-states">
                  <span class="demo-text-btn">文字按钮</span>
                  <span class="demo-text-btn hover">文字悬浮</span>
                  <span class="demo-text-btn active-s">文字点击</span>
                  <span class="demo-text-btn disabled">文字禁用</span>
                </div>
              </div>
              <div>
                <h5 class="mb-3">文字大小</h5>
                <div class="tags">
                  <span class="tag" v-for="(h,i) in componentConfig.buttons.text.heights" :key="'th'+i">{{ h }} <span class="tag-rm" @click="componentConfig.buttons.text.heights.splice(i,1)">✕</span></span>
                  <span class="tag-add" @click="addArrayItem($event, componentConfig.buttons.text.heights,'16px')">+ 添加</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ====== 数据录入类组件 ====== -->
        <div v-if="activeTab === 'comp_input'" class="form-container">
          <p class="comp-desc">本规范基于 Global Foundation 的核心规范框架，旨在为设计师与开发者提供高度统一一致、历经反复专业内构建规范。</p>

          <!-- 1. 输入组件 -->
          <div class="section-title"><span class="section-num">◈ 1.</span> 输入组件</div>
          <div class="grid-2 mb-4 align-start">
            <!-- 01 输入框 -->
            <div class="card">
              <div class="comp-badge">01 输入框</div>
              <div class="form-group mt-3">
                <label>高度 (px)</label>
                <div class="tags">
                  <span class="tag" v-for="(h,i) in componentConfig.inputs.text.height" :key="'th'+i">{{ h }} <span class="tag-rm" @click="componentConfig.inputs.text.height.splice(i,1)">✕</span></span>
                  <span class="tag-add" @click="addArrayItem($event, componentConfig.inputs.text.height,'40')">+ 添加</span>
                </div>
              </div>
              <div class="form-group">
                <label>圆角 (px)</label>
                <div class="tags">
                  <span class="tag" v-for="(r,i) in componentConfig.inputs.text.radius" :key="'tr'+i">{{ r }} <span class="tag-rm" @click="componentConfig.inputs.text.radius.splice(i,1)">✕</span></span>
                  <span class="tag-add" @click="addArrayItem($event, componentConfig.inputs.text.radius,'6')">+ 添加</span>
                </div>
              </div>
              <div class="form-group">
                <label>内边距 (px)</label>
                <div class="tags">
                  <span class="tag" v-for="(p,i) in componentConfig.inputs.text.padding" :key="'tp'+i">{{ p }} <span class="tag-rm" @click="componentConfig.inputs.text.padding.splice(i,1)">✕</span></span>
                  <span class="tag-add" @click="addArrayItem($event, componentConfig.inputs.text.padding,'16')">+ 添加</span>
                </div>
              </div>
              <h5 class="mt-3 mb-2">交互状态色值</h5>
              <div class="state-color-grid">
                <div class="scg-item"><div class="demo-input normal">输入框文字</div><span class="scg-label">常规 #C0C0E3</span></div>
                <div class="scg-item"><div class="demo-input focus">聚焦中...</div><span class="scg-label">聚焦 #1A6AFF</span></div>
                <div class="scg-item"><div class="demo-input error">错误信息</div><span class="scg-label">错误 #F97F7F</span></div>
                <div class="scg-item"><div class="demo-input disabled-i" disabled>禁用</div><span class="scg-label">禁用 #F5F7F9</span></div>
              </div>
            </div>
            <!-- 02 数字输入框 -->
            <div class="card">
              <div class="comp-badge">02 数字输入框</div>
              <p class="desc mt-2">单组件 (包含 输入框 高度、宽度、内边距、交互状态色值) 同步 输入框 规范。</p>
              <h5 class="mt-3 mb-2">名牌操作按钮色值规范</h5>
              <div class="form-group">
                <label>操作按钮宽度 (px)</label>
                <div class="tags">
                  <span class="tag" v-for="(w,i) in componentConfig.inputs.number.opWidth" :key="'nw'+i">{{ w }} <span class="tag-rm" @click="componentConfig.inputs.number.opWidth.splice(i,1)">✕</span></span>
                  <span class="tag-add" @click="addArrayItem($event, componentConfig.inputs.number.opWidth,'28')">+ 添加</span>
                </div>
              </div>
              <div class="form-group">
                <label>最大输入值</label>
                <input type="text" v-model="componentConfig.inputs.number.maxVal" />
              </div>
            </div>
          </div>

          <!-- 2. 选择组件 -->
          <div class="section-title"><span class="section-num">◈ 2.</span> 选择组件</div>
          <div class="grid-2 mb-4 align-start">
            <!-- 03 选择器 -->
            <div class="card">
              <div class="comp-badge">03 选择器</div>
              <p class="desc mt-2">单组件 (包含 输入框 高度、宽度、内边距、交互状态色值) 同步 输入框 规范。</p>
              <h5 class="mt-3 mb-2">其他元素规范</h5>
              <div class="form-group">
                <label>下拉箭头图标尺寸 (px)</label>
                <div class="tags">
                  <span class="tag" v-for="(s,i) in componentConfig.inputs.select.arrowSize" :key="'as'+i">{{ s }} <span class="tag-rm" @click="componentConfig.inputs.select.arrowSize.splice(i,1)">✕</span></span>
                  <span class="tag-add" @click="addArrayItem($event, componentConfig.inputs.select.arrowSize,'28')">+ 添加</span>
                </div>
              </div>
            </div>
            <!-- 04 日期选择器 -->
            <div class="card">
              <div class="comp-badge">04 日期选择器</div>
              <p class="desc mt-2">单组件 (包含 输入框 高度、宽度、内边距、交互状态色值) 同步 输入框 规范。</p>
              <h5 class="mt-3 mb-2">其他元素规范</h5>
              <div class="form-group">
                <label>选中日期背景色</label>
                <div class="color-row-item">
                  <div class="color-box" style="background:#1A6AFF"></div>
                  <span style="font-size:13px;color:#1a1d2e;">#1A6AFF</span>
                </div>
              </div>
              <div class="form-group">
                <label>今日标记色</label>
                <div class="color-row-item">
                  <div class="color-box" style="background:#1A6AFF"></div>
                  <span style="font-size:13px;color:#1a1d2e;">#1A6AFF</span>
                </div>
              </div>
            </div>
          </div>

          <div class="grid-2 mb-4 align-start">
            <!-- 05 单选 -->
            <div class="card">
              <div class="comp-badge">05 单选</div>
              <div class="form-group mt-3">
                <label>ICON尺寸 (px)</label>
                <div class="tags">
                  <span class="tag" v-for="(s,i) in componentConfig.inputs.radio.sizes" :key="'rs'+i">{{ s }} <span class="tag-rm" @click="componentConfig.inputs.radio.sizes.splice(i,1)">✕</span></span>
                  <span class="tag-add" @click="addArrayItem($event, componentConfig.inputs.radio.sizes,'20')">+ 添加</span>
                </div>
              </div>
              <div class="state-color-grid mt-2">
                <div class="scg-item"><div class="demo-radio uncheck"></div><span class="scg-label">未选 #C0C0E3</span></div>
                <div class="scg-item"><div class="demo-radio checked"></div><span class="scg-label">选中 #1A6AFF</span></div>
                <div class="scg-item"><div class="demo-radio disabled-r"></div><span class="scg-label">禁用 #F5F7F9</span></div>
              </div>
            </div>
            <!-- 06 多选 -->
            <div class="card">
              <div class="comp-badge">06 多选</div>
              <div class="form-group mt-3">
                <label>ICON尺寸 (px)</label>
                <div class="tags">
                  <span class="tag" v-for="(s,i) in componentConfig.inputs.checkbox.sizes" :key="'cs'+i">{{ s }} <span class="tag-rm" @click="componentConfig.inputs.checkbox.sizes.splice(i,1)">✕</span></span>
                  <span class="tag-add" @click="addArrayItem($event, componentConfig.inputs.checkbox.sizes,'20')">+ 添加</span>
                </div>
              </div>
              <div class="state-color-grid mt-2">
                <div class="scg-item"><div class="demo-checkbox uncheck"></div><span class="scg-label">未选 #C0C0E3</span></div>
                <div class="scg-item"><div class="demo-checkbox checked"></div><span class="scg-label">选中 #1A6AFF</span></div>
                <div class="scg-item"><div class="demo-checkbox disabled-c"></div><span class="scg-label">禁用 #F5F7F9</span></div>
              </div>
            </div>
          </div>

          <!-- 3. 开关与表单 -->
          <div class="section-title"><span class="section-num">◈ 3.</span> 开关与表单</div>
          <div class="card mb-4">
            <div class="comp-badge">07 开关</div>
            <div class="form-group mt-3">
              <label>ICON尺寸 (px)</label>
              <div class="tags">
                <span class="tag" v-for="(s,i) in componentConfig.inputs.switch.sizes" :key="'ss'+i">{{ s }} <span class="tag-rm" @click="componentConfig.inputs.switch.sizes.splice(i,1)">✕</span></span>
                <span class="tag-add" @click="addArrayItem($event, componentConfig.inputs.switch.sizes,'44*22px')">+ 添加</span>
              </div>
            </div>
            <div class="grid-2 mt-3">
              <div>
                <div class="form-row"><span>开启背景色</span></div>
                <div class="color-row-item mt-1"><div class="color-box" style="background:#1A6AFF"></div><span style="font-size:13px;">#1A6AFF</span></div>
                <div class="form-row mt-2"><span>开启内圆色</span></div>
                <div class="color-row-item mt-1"><div class="color-box" style="background:#FFFFFF;border:1px solid #e2e4ec"></div><span style="font-size:13px;">#FFFFFF</span></div>
              </div>
              <div>
                <div class="form-row"><span>关闭背景色</span></div>
                <div class="color-row-item mt-1"><div class="color-box" style="background:#C0C0E3"></div><span style="font-size:13px;">#C0C0E3</span></div>
                <div class="form-row mt-2"><span>关闭内圆色</span></div>
                <div class="color-row-item mt-1"><div class="color-box" style="background:#707CDC"></div><span style="font-size:13px;">#707CDC</span></div>
              </div>
            </div>
          </div>
        </div>

        <!-- ====== 数据展示与导航组件 ====== -->
        <div v-if="activeTab === 'comp_nav'" class="form-container">
          <p class="comp-desc">本规范基于 Global Foundation 的核心规范框架，旨在为设计师与开发者提供高度统一一致、历经反复专业内构建规范。</p>

          <!-- 1. 导航类组件 -->
          <div class="section-title"><span class="section-num">◈ 1.</span> 导航类组件</div>
          <div class="grid-2 mb-4 align-start">
            <!-- 01 导航栏 -->
            <div class="card">
              <div class="comp-badge">01 导航栏</div>
              <div class="form-group mt-3">
                <label>高度 (px)</label>
                <div class="tags">
                  <span class="tag" v-for="(h,i) in componentConfig.display.nav.height" :key="'nh'+i">{{ h }} <span class="tag-rm" @click="componentConfig.display.nav.height.splice(i,1)">✕</span></span>
                  <span class="tag-add" @click="addArrayItem($event, componentConfig.display.nav.height,'48')">+ 添加</span>
                </div>
              </div>
              <div class="form-group">
                <label>圆角 (px)</label>
                <div class="tags">
                  <span class="tag" v-for="(r,i) in componentConfig.display.nav.radius" :key="'nr'+i">{{ r }} <span class="tag-rm" @click="componentConfig.display.nav.radius.splice(i,1)">✕</span></span>
                  <span class="tag-add" @click="addArrayItem($event, componentConfig.display.nav.radius,'4')">+ 添加</span>
                </div>
              </div>
              <div class="form-group">
                <label>内边距 (px)</label>
                <div class="tags">
                  <span class="tag" v-for="(p,i) in componentConfig.display.nav.padding" :key="'np'+i">{{ p }} <span class="tag-rm" @click="componentConfig.display.nav.padding.splice(i,1)">✕</span></span>
                  <span class="tag-add" @click="addArrayItem($event, componentConfig.display.nav.padding,'16')">+ 添加</span>
                </div>
              </div>
              <h5 class="mt-3 mb-2">激活状态色</h5>
              <div class="color-row-item">
                <div class="color-box" style="background:#1A6AFF"></div>
                <div>
                  <div style="font-size:13px;font-weight:600;">Hover 状态</div>
                  <div style="font-size:12px;color:#6b7280;">#EAF2FF</div>
                </div>
              </div>
              <div class="color-row-item mt-2">
                <div class="color-box" style="background:#EAF2FF"></div>
                <div>
                  <div style="font-size:13px;font-weight:600;">选中状态</div>
                  <div style="font-size:12px;color:#6b7280;">#EAF2FF</div>
                </div>
              </div>
            </div>
            <!-- 02 面包屑 + 03 分页 -->
            <div style="display:flex;flex-direction:column;gap:16px;">
              <div class="card">
                <div class="comp-badge">02 面包屑</div>
                <div class="form-group mt-3">
                  <label>间隔符间距 (px)</label>
                  <div class="tags">
                    <span class="tag" v-for="(s,i) in componentConfig.display.breadcrumb.separatorSpacing" :key="'bs'+i">{{ s }} <span class="tag-rm" @click="componentConfig.display.breadcrumb.separatorSpacing.splice(i,1)">✕</span></span>
                    <span class="tag-add" @click="addArrayItem($event, componentConfig.display.breadcrumb.separatorSpacing,'12')">+ 添加</span>
                  </div>
                </div>
              </div>
              <div class="card">
                <div class="comp-badge">03 分页</div>
                <div class="form-group mt-3">
                  <label>高度 (px)</label>
                  <div class="tags">
                    <span class="tag" v-for="(h,i) in componentConfig.display.pagination.height" :key="'ph'+i">{{ h }} <span class="tag-rm" @click="componentConfig.display.pagination.height.splice(i,1)">✕</span></span>
                    <span class="tag-add" @click="addArrayItem($event, componentConfig.display.pagination.height,'32')">+ 添加</span>
                  </div>
                </div>
                <div class="form-group">
                  <label>圆角 (px)</label>
                  <div class="tags">
                    <span class="tag" v-for="(r,i) in componentConfig.display.pagination.radius" :key="'pr2'+i">{{ r }} <span class="tag-rm" @click="componentConfig.display.pagination.radius.splice(i,1)">✕</span></span>
                    <span class="tag-add" @click="addArrayItem($event, componentConfig.display.pagination.radius,'4')">+ 添加</span>
                  </div>
                </div>
                <h5 class="mt-3 mb-2">页码元素色值规范</h5>
                <div class="form-row"><span style="font-size:13px;">激活页码背景</span><div class="color-box" style="background:#1A6AFF; width:20px; height:20px; border-radius:3px;"></div></div>
                <div class="form-row mt-1"><span style="font-size:13px;">激活页码文字</span><div class="color-box" style="background:#FFFFFF;border:1px solid #e2e4ec; width:20px; height:20px; border-radius:3px;"></div></div>
              </div>
            </div>
          </div>

          <!-- 2. 数据类组件 -->
          <div class="section-title"><span class="section-num">◈ 2.</span> 数据类组件</div>
          <div class="grid-2 mb-4 align-start">
            <!-- 04 表格 -->
            <div class="card">
              <div class="comp-badge">04 表格</div>
              <div class="form-group mt-3">
                <label>行高 (px)</label>
                <div class="tags">
                  <span class="tag" v-for="(h,i) in componentConfig.display.table.rowHeight" :key="'trh'+i">{{ h }} <span class="tag-rm" @click="componentConfig.display.table.rowHeight.splice(i,1)">✕</span></span>
                  <span class="tag-add" @click="addArrayItem($event, componentConfig.display.table.rowHeight,'48')">+ 添加</span>
                </div>
              </div>
              <div class="form-row mt-3" @click="componentConfig.checkTableAlignment = !componentConfig.checkTableAlignment">
                <label>数字右对齐 / 文本左对齐检查</label>
                <div class="toggle" :class="{on: componentConfig.checkTableAlignment}"></div>
              </div>
            </div>
            <!-- 05 标签 -->
            <div class="card">
              <div class="comp-badge">05 标签 (Tag)</div>
              <div class="form-group mt-3">
                <label>高度 (px)</label>
                <div class="tags">
                  <span class="tag" v-for="(h,i) in componentConfig.display.tag.height" :key="'tgh'+i">{{ h }} <span class="tag-rm" @click="componentConfig.display.tag.height.splice(i,1)">✕</span></span>
                  <span class="tag-add" @click="addArrayItem($event, componentConfig.display.tag.height,'24')">+ 添加</span>
                </div>
              </div>
              <div class="form-group">
                <label>圆角 (px)</label>
                <div class="tags">
                  <span class="tag" v-for="(r,i) in componentConfig.display.tag.radius" :key="'tgr'+i">{{ r }} <span class="tag-rm" @click="componentConfig.display.tag.radius.splice(i,1)">✕</span></span>
                  <span class="tag-add" @click="addArrayItem($event, componentConfig.display.tag.radius,'4')">+ 添加</span>
                </div>
              </div>
              <div class="form-group">
                <label>内边距 (px)</label>
                <div class="tags">
                  <span class="tag" v-for="(p,i) in componentConfig.display.tag.padding" :key="'tgp'+i">{{ p }} <span class="tag-rm" @click="componentConfig.display.tag.padding.splice(i,1)">✕</span></span>
                  <span class="tag-add" @click="addArrayItem($event, componentConfig.display.tag.padding,'8')">+ 添加</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 3. 状态与反馈 -->
          <div class="section-title"><span class="section-num">◈ 3.</span> 状态与反馈</div>
          <div class="card mb-4">
            <div class="comp-badge">06 弹框 (Modal)</div>
            <div class="grid-2 mt-3 align-start">
              <div>
                <div class="form-group">
                  <label>遮罩层透明度</label>
                  <input type="text" v-model="componentConfig.display.modal.maskOpacity" />
                </div>
                <div class="form-group">
                  <label>标题区高度 (px)</label>
                  <div class="tags">
                    <span class="tag" v-for="(h,i) in componentConfig.display.modal.headHeight" :key="'mh'+i">{{ h }} <span class="tag-rm" @click="componentConfig.display.modal.headHeight.splice(i,1)">✕</span></span>
                    <span class="tag-add" @click="addArrayItem($event, componentConfig.display.modal.headHeight,'52')">+ 添加</span>
                  </div>
                </div>
              </div>
              <div>
                <div class="form-group">
                  <label>内容区内边距 (px)</label>
                  <div class="tags">
                    <span class="tag" v-for="(p,i) in componentConfig.display.modal.contentPadding" :key="'mp'+i">{{ p }} <span class="tag-rm" @click="componentConfig.display.modal.contentPadding.splice(i,1)">✕</span></span>
                    <span class="tag-add" @click="addArrayItem($event, componentConfig.display.modal.contentPadding,'24')">+ 添加</span>
                  </div>
                </div>
                <div class="form-group">
                  <label>标题 Top 间距 (px)</label>
                  <input type="text" v-model="componentConfig.display.modal.titleHeight" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'design'" class="form-container">
          <div class="section-title mt-4">
            <span class="section-icon" aria-hidden="true"><IconStroke name="ruler" size="md" /></span>
            对比区域设置
          </div>
          <div class="card">
             <div class="grid-2">
               <div class="form-group">
                 <label>截图宽度 (px)</label>
                 <div class="input-with-unit"><input type="number" v-model="designConfig.compareWidth" /><span>px</span></div>
               </div>
               <div class="form-group">
                 <label>设备类型</label>
                 <select v-model="designConfig.deviceType">
                    <option value="桌面端">桌面端 (Desktop)</option>
                    <option value="移动端">移动端 (Mobile)</option>
                 </select>
               </div>
             </div>
             <div class="form-group mt-3">
               <label>色差容忍阈值</label>
               <input type="range" v-model="designConfig.colorThreshold" min="0" max="100" class="w-100" />
               <small>建议初始值 10%。当前: {{designConfig.colorThreshold}}%</small>
             </div>
          </div>

          <div class="section-title mt-4">
            <span class="section-icon" aria-hidden="true"><IconStroke name="chip-ai" size="md" /></span>
            AI 智能分析
          </div>
          <div class="card">
             <div class="form-row" @click="designConfig.aiAnalysis = !designConfig.aiAnalysis">
               <label>启用 AI 差异分析<br/><small>自动识别布局偏移、色值差异等</small></label>
               <div class="toggle" :class="{on: designConfig.aiAnalysis}"></div>
             </div>
             <div class="form-row mt-3" @click="designConfig.aiSummary = !designConfig.aiSummary">
               <label>生成走查报告摘要<br/><small>自动生成一份可读性强的问题摘要报告</small></label>
               <div class="toggle" :class="{on: designConfig.aiSummary}"></div>
             </div>
          </div>

          <div class="section-title mt-4">
            <span class="section-icon" aria-hidden="true"><IconStroke name="crosshair" size="md" /></span>
            对比精度设置
          </div>
          <div class="card mb-4">
             <div class="precision-tabs">
                <div class="precision-opt" :class="{ active: designConfig.precisionMode === 'pixel' }" @click="designConfig.precisionMode = 'pixel'">
                  <div class="precision-radio"></div>
                  <div>
                    <div class="precision-opt-name">像素级对比</div>
                    <div class="precision-opt-desc">严格校验每一个像素的差异</div>
                  </div>
                </div>
                <div class="precision-opt" :class="{ active: designConfig.precisionMode === 'visual' }" @click="designConfig.precisionMode = 'visual'">
                  <div class="precision-radio"></div>
                  <div>
                    <div class="precision-opt-name">视觉语义</div>
                    <div class="precision-opt-desc">基于视觉感官忽略微小偏移</div>
                  </div>
                </div>
             </div>

             <div class="ignore-grid" style="border-top:1px dashed #e8eaf0; padding-top:20px;">
                <div>
                  <div class="check-group-title">忽略区域设置</div>
                  <label class="checkbox-item"><input type="checkbox" v-model="designConfig.ignoreStatus"> 状态栏</label>
                  <label class="checkbox-item"><input type="checkbox" v-model="designConfig.ignoreAds"> 动态广告位</label>
                </div>
                <div>
                  <div class="check-group-title">自动对齐锚点</div>
                  <div class="anchor-grid">
                    <div v-for="i in 9" :key="i" class="anchor-dot" :class="{ active: designConfig.anchor === i - 1 }" @click="designConfig.anchor = i - 1"></div>
                  </div>
                </div>
             </div>
          </div>
        </div>

        
        <div class="footer-actions config-footer-dock" aria-label="配置操作">
           <button class="btn-ghost" @click="cancelEdit">取消</button>
           <button class="btn-primary" :disabled="!isDirty" @click="saveEdit">保存配置</button>
        </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import AppNavbar from '../components/AppNavbar.vue'
import IconStroke from '../components/IconStroke.vue'
import SpecAddFloat from '../components/SpecAddFloat.vue'
import SpecColorFloat from '../components/SpecColorFloat.vue'
import FilterSelect from '../components/FilterSelect.vue'
import { Swal, showToastSuccess, showToastInfo } from '../utils/modal'
import axios from 'axios'
import { useUserStore } from '../store/user'
import { openSpecAddPanel, confirmSpecAddPanel, openColorEditPanel } from '../utils/specModal'
import { normalizeResponsiveBreakpoints } from '../utils/baselineConfig'
import { normalizeAsciiPunctuation } from '../utils/punctuationNormalize'

const userStore = useUserStore()
const activeTab = ref('baseline')
const expandComponents = ref(false)

const headerTitle = computed(() => {
  if (activeTab.value === 'baseline') return '基准值模式'
  if (activeTab.value === 'comp_global') return '全局基础规范'
  if (activeTab.value === 'comp_btn') return '按钮组件'
  if (activeTab.value === 'comp_input') return '数据录入类组件'
  if (activeTab.value === 'comp_nav') return '数据展示与导航组件'
  if (activeTab.value === 'design') return '设计稿模式'
  return ''
})

const currentGlobalEnable = computed(() => {
  if (activeTab.value === 'baseline') return baselineConfig.globalEnable
  if (activeTab.value.startsWith('comp_')) return componentConfig.globalEnable
  return designConfig.globalEnable
})

const toggleGlobalEnable = () => {
  if (activeTab.value === 'baseline') baselineConfig.globalEnable = !baselineConfig.globalEnable
  else if (activeTab.value.startsWith('comp_')) componentConfig.globalEnable = !componentConfig.globalEnable
  else designConfig.globalEnable = !designConfig.globalEnable
}

const toggleComponentMenu = () => {
  expandComponents.value = !expandComponents.value
  if (!activeTab.value.startsWith('comp_')) {
    activeTab.value = 'comp_global'
  }
}

const textOverflowOptions = [
  { value: '默认使用省略号', label: '默认使用省略号' },
  { value: '换行显示', label: '换行显示' }
]

// Reactive configuration objects
const defaultBaseline = {
  colors: [
    { hex: '#1A6AFF', label: '主题色' },
    { hex: '#4787FF', label: 'hover色' },
    { hex: '#145BD7', label: '点击色' }
  ],
  colorThreshold: '< 2ΔE',
  fontFamily: '微软雅黑, PingFang SC',
  fontSizes: '32, 16, 14, 12',
  lineHeights: '1.2, 1.5, 1.6',
  fontWeights: '400, 600',
  spacingTokens: ['4px', '8px', '16px'],
  gridCheck: true,
  gridTokens: ['8px'],
  radiusCheck: true,
  radiusTokens: ['4px', '8px', '12px'],
  transitionCheck: true,
  transitions: '0.2s, 0.3s',
  buttonHeightCheck: true,
  inputSelectHeightCheck: true,
  buttonHeightTokens: ['32px', '40px'],
  inputHeightTokens: ['32px', '40px'],
  shadowCheck: true,
  shadowPreset: '符合 Ant Design 投影规范',
  iconCheck: true,
  iconTokens: ['14*14px', '16*16px'],
  iconStyleCheck: true,
  iconStrokeTokens: ['1.5px', '2px'],
  minClickArea: 44,
  hoverCheck: true,
  gestureCheck: true,
  textOverflow: '默认使用省略号',
  responsiveCheck: true,
  responsiveBreakpoints: ['768px', '1024px', '1440px'],
  zIndexCheck: true,
  emptyStateCheck: true,
  loadingStateCheck: true,
  contrastCheck: true,
  altCheck: true,
  domSemantics: true,
  focusOrder: true,
  imageSizeLimit: 44,
  hardcodeCheck: true,
  deadlinkCheck: true,
  textFormatCheck: true,
  globalEnable: true
}

const defaultDesign = {
  globalEnable: true,
  uploadedFile: null,
  compareWidth: 1440,
  deviceType: '桌面端',
  colorThreshold: 10,
  aiAnalysis: true,
  aiSummary: true,
  precisionMode: 'pixel',
  ignoreStatus: true,
  ignoreAds: false,
  anchor: 0
}

const defaultComponent = {
  globalEnable: true,
  // 1. 全局基础规范
  brandColors: [
    { label: '常规', hex: '#1A6AFF', desc: '选中态、高亮、主按钮等常规核心元素' },
    { label: '悬浮', hex: '#256AF4', desc: '主色元素的鼠标悬停交互' },
    { label: '点击', hex: '#145BD7', desc: '主色元素的鼠标按下交互' },
    { label: '禁用', hex: '#A3C3FF', desc: '常规色的禁用状态的颜色' },
    { label: '浅色1', hex: '#EFF1F7', desc: '二级按钮点击状态色、框下背景色' },
    { label: '浅色2', hex: '#EAF2FF', desc: '左侧导航条悬停状态、选中状态' }
  ],
  neutralColors: [
    { label: '背景与分割线 1', hex: '#F5F7F9' },
    { label: '背景与分割线 2', hex: '#CDD3E3' },
    { label: '分割线 3', hex: '#E9EBEF' }
  ],
  textColors: {
    primary: '#101010', secondary: '#1F1F21', light1: '#3E3F43', 
    light2: '#707E87', light3: '#9D9EA9', light4: '#FFFFFF'
  },
  spacing: ['4px', '8px', '12px', '16px', '24px'],
  grid: ['8px', '10px', '24px'],
  typography: {
    family: '微软雅黑, PingFang SC',
    sizes: '32, 16, 14, 12',
    lineHeights: '1.2, 1.5, 1.6',
    weights: '400, 600',
    spacingTokens: ['4px', '8px', '16px']
  },
  shadowPreset: '符合 Ant Design 投影规范',
  icons: {
    sizes: ['14*14px', '16*16px'],
    strokes: ['1.5px', '2px'],
    radius: ['4px', '6px', '12px']
  },

  // 2. 按钮组件
  buttons: {
    primary: { height: ['32px', '20px'], radius: ['4px', '2px'], padding: ['20px', '16px', '30px', '32px'] },
    secondary: { height: ['32px', '20px'], radius: ['4px', '2px'], padding: ['20px', '16px', '30px', '32px'] },
    dashed: { height: ['32px', '20px'], radius: ['4px', '2px'], padding: ['20px', '16px', '30px', '32px'] },
    text: { heights: ['12px', '14px'] }
  },

  // 3. 数据录入类
  inputs: {
    text: { height: ['32', '20'], radius: ['2', '4', '8'], padding: ['8', '10', '12'] },
    number: { opWidth: ['24', '32'], maxVal: '200000' },
    select: { arrowSize: ['24', '32'] },
    radio: { sizes: ['14', '16', '18'] },
    checkbox: { sizes: ['14', '16', '18'] },
    switch: { sizes: ['52*26px', '40*20px'] }
  },

  // 4. 数据展示与导航
  display: {
    nav: { height: ['40', '46', '52'], radius: ['2', '4', '8'], padding: ['8', '10', '12'] },
    breadcrumb: { separatorSpacing: ['6', '8', '10'] },
    pagination: { height: ['40', '46', '52'], radius: ['2', '4', '8'] },
    table: { rowHeight: ['32', '40'] },
    tag: { height: ['40', '46', '52'], radius: ['2', '4', '8'], padding: ['8', '10', '12'] },
    modal: { maskOpacity: '30%', titleHeight: '8px', headHeight: ['40', '46', '52'], contentPadding: ['20', '24', '30', '32px'] }
  }
}

// 初始化配置为空
const baselineConfig = reactive(JSON.parse(JSON.stringify(defaultBaseline)))
const designConfig = reactive(JSON.parse(JSON.stringify(defaultDesign)))
const componentConfig = reactive(JSON.parse(JSON.stringify(defaultComponent)))

/** 列表类文本：中文输入法全角标点转半角，与走查解析一致 */
const normBaselineListFields = () => {
  ;['transitions', 'fontFamily', 'fontSizes', 'lineHeights', 'fontWeights'].forEach((k) => {
    if (baselineConfig[k] != null && baselineConfig[k] !== '') {
      baselineConfig[k] = normalizeAsciiPunctuation(baselineConfig[k])
    }
  })
}

const isDirty = ref(false)

const specFloat = reactive({
  open: false,
  left: 0,
  top: 0,
  title: '',
  fieldLabel: '规范值',
  defaultVal: '',
  mode: 'plain',
  arr: null,
})

const colorFloat = reactive({
  open: false,
  left: 0,
  top: 0,
  title: '修改色值',
  label: '',
  hex: '#000000',
  editIdx: null,
  /** true：添加色值；false：编辑已有行 */
  isAdd: false,
})

onMounted(async () => {
  if (userStore.userInfo) {
    try {
      const res = await axios.get(`http://localhost:8000/api/config/${userStore.userInfo.id}`)
      if (res.data.status === 'success' && res.data.data) {
        if (res.data.data.baseline_config) {
          Object.assign(baselineConfig, res.data.data.baseline_config)
          normalizeResponsiveBreakpoints(baselineConfig)
        }
        if (res.data.data.design_config) Object.assign(designConfig, res.data.data.design_config)
        if (res.data.data.component_config) Object.assign(componentConfig, res.data.data.component_config)
      }
    } catch (e) {
      console.error('获取远端配置失败:', e)
    }
  }
  // 初始化完成后再监听变化
  setTimeout(() => {
    watch([baselineConfig, designConfig, componentConfig], () => {
      isDirty.value = true
    }, { deep: true })
  }, 100)
})

const addToken = (e, arr, val, title) => openSpecAddPanel(specFloat, e, arr, val, title || '添加规范值')

const addArrayItem = (e, arr, val, title) => openSpecAddPanel(specFloat, e, arr, val, title || '添加规范值')

const onSpecFloatConfirm = (val) => confirmSpecAddPanel(specFloat, val)

const onColorFloatConfirm = (payload) => {
  if (!payload) return
  if (colorFloat.isAdd) {
    const hex = String(payload.hex || '').trim().toUpperCase()
    const dup = baselineConfig.colors.some((c) => String(c.hex || '').trim().toUpperCase() === hex)
    if (dup) {
      showToastInfo('已存在相同的色值')
      colorFloat.editIdx = null
      colorFloat.isAdd = false
      return
    }
    baselineConfig.colors.push({
      label: payload.label?.trim() || '新增色值',
      hex: payload.hex,
    })
  } else {
    const i = colorFloat.editIdx
    if (i != null && baselineConfig.colors[i]) {
      baselineConfig.colors[i].label = payload.label
      baselineConfig.colors[i].hex = payload.hex
    }
  }
  colorFloat.editIdx = null
  colorFloat.isAdd = false
}

const removeToken = (arr, idx) => {
  arr.splice(idx, 1)
}


const cancelEdit = async () => {
  if (userStore.userInfo) {
    try {
      const res = await axios.get(`http://localhost:8000/api/config/${userStore.userInfo.id}`)
      if (res.data.status === 'success' && res.data.data) {
        Object.assign(baselineConfig, res.data.data.baseline_config || defaultBaseline)
        normalizeResponsiveBreakpoints(baselineConfig)
        Object.assign(designConfig, res.data.data.design_config || defaultDesign)
        Object.assign(componentConfig, res.data.data.component_config || defaultComponent)
      } else {
        Object.assign(baselineConfig, JSON.parse(JSON.stringify(defaultBaseline)))
        normalizeResponsiveBreakpoints(baselineConfig)
        Object.assign(designConfig, JSON.parse(JSON.stringify(defaultDesign)))
        Object.assign(componentConfig, JSON.parse(JSON.stringify(defaultComponent)))
      }
    } catch (e) {
      Object.assign(baselineConfig, JSON.parse(JSON.stringify(defaultBaseline)))
      normalizeResponsiveBreakpoints(baselineConfig)
      Object.assign(designConfig, JSON.parse(JSON.stringify(defaultDesign)))
      Object.assign(componentConfig, JSON.parse(JSON.stringify(defaultComponent)))
    }
  }
  setTimeout(() => isDirty.value = false, 0)
}

const saveEdit = async () => {
  if (!userStore.userInfo) return Swal.fire('错误', '请先登录', 'error')
  normBaselineListFields()
  try {
    const res = await axios.post('http://localhost:8000/api/config', {
      user_id: userStore.userInfo.id,
      baseline_config: baselineConfig,
      design_config: designConfig,
      component_config: componentConfig
    })
    
    if (res.data.status === 'success') {
      isDirty.value = false
      showToastSuccess('配置已保存')
    }
  } catch(e) {
    Swal.fire('保存失败', '请求错误', 'error')
  }
}


const editColor = (e, idx) => {
  const color = baselineConfig.colors[idx]
  colorFloat.isAdd = false
  colorFloat.editIdx = idx
  openColorEditPanel(colorFloat, e, color.label, color.hex, '修改色值')
}

const addColor = (e) => {
  colorFloat.isAdd = true
  colorFloat.editIdx = null
  openColorEditPanel(colorFloat, e, '新增色值', '#000000', '添加色值')
}
</script>

<style scoped>
.page-container { background: #f4f6fb; min-height: 100vh; padding-top: 60px; padding-bottom: 0; overflow: hidden; }
.config-layout { display: flex; max-width: 1440px; margin: 0 auto; height: calc(100vh - 60px); overflow: hidden; }
.sidebar { width: 260px; background: #fff; padding: 20px; border-right: 1px solid #e2e4ec; overflow-y: auto; flex-shrink: 0; }
.sidebar-title { font-size: 14px; color: #9ca3af; margin-bottom: 16px; font-weight: bold; }
.nav-item { padding: 12px 16px; margin-bottom: 4px; border-radius: 8px; cursor: pointer; color: #4b5563; display: flex; align-items: center; font-weight: 500;}
.nav-item:hover { background: #f9fafb; }
.nav-item.active { background: #eef2ff; color: #1A6AFF; font-weight: bold; }
.nav-item .icon { margin-right: 10px; display: inline-flex; align-items: center; justify-content: center; color: inherit; }
.nav-chevron { transition: transform 0.2s ease; color: #9ca3af !important; display: inline-flex !important; }
.nav-chevron.open { transform: rotate(180deg); }
.sub-nav { padding-left: 40px; margin-bottom: 10px; }
.sub-item { padding: 8px 0; color: #6b7280; font-size: 14px; cursor: pointer; }
.sub-item:hover { color: #1A6AFF; }
.arrow { margin-left: auto; font-size: 12px; color: #9ca3af;}

.main-content { flex: 1; overflow-y: auto; display: flex; flex-direction: column; background: #f4f6fb; padding: 16px 20px 24px; box-sizing: border-box; }

.config-panel-sheet {
  background: #fff;
  border: 1px solid #e8eaef;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(15, 23, 42, 0.04);
  flex: 0 0 auto;
  align-self: stretch;
  width: 100%;
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 60px - 48px);
  /* 为吸底操作栏预留空间，避免正文被遮挡 */
  padding-bottom: 88px;
  box-sizing: border-box;
}
.config-panel-sheet .content-header {
  padding: 22px 28px 18px;
  border-bottom: 1px solid #f0f1f5;
}
.content-header-inner { width: 100%; min-width: 0; }
.content-header-title-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}
.content-header-h2 {
  margin: 0;
  font-size: 24px;
  color: #1a1d2e;
  line-height: 1.25;
  flex: 1;
  min-width: 0;
}
.form-container { padding: 0 40px; }
.config-panel-sheet .form-container {
  padding: 20px 28px 30px;
  flex: 0 0 auto;
}

.breadcrumb { font-size: 13px; color: #9ca3af; margin-bottom: 8px; }
.breadcrumb .cur { color: #1a1d2e; font-weight: bold; }
h2 { margin: 0; font-size: 24px; color: #1a1d2e; }
.subtitle { margin: 6px 0 0 0; color: #6b7280; font-size: 14px; }

.toggle-group-top {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  background: white;
  padding: 6px 12px;
  border-radius: 20px;
  border: 1px solid #e2e4ec;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
  cursor: pointer;
}
.toggle-group-top-label {
  font-size: 14px;
  font-weight: bold;
  color: #1a1d2e;
  margin-right: 8px;
  line-height: 1;
}

.section-title { font-size: 18px; font-weight: bold; color: #1a1d2e; margin-bottom: 16px; display: flex; align-items: center; }
.section-title .section-icon { display: inline-flex; align-items: center; justify-content: center; margin-right: 10px; color: currentColor; }
.card-hd-with-icon { display: flex; align-items: center; gap: 8px; margin: 0 0 16px 0; font-size: 15px; color: #1a1d2e; }
.card-hd-icon { display: inline-flex; color: currentColor; flex-shrink: 0; }
.a11y-card { display: flex; flex-direction: column; min-height: 168px; }
.a11y-card .a11y-desc { flex: 1; }
.a11y-footer { margin-top: auto; padding-top: 12px; display: flex; justify-content: flex-end; }
.contrast-row { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; margin-top: 4px; }
.contrast-ratio { font-size: 1.35rem; font-weight: 800; line-height: 1.2; margin: 0 !important; }
.mt-4 { margin-top: 24px; }
.mt-3 { margin-top: 16px; }
.mt-2 { margin-top: 8px; }
.mb-4 { margin-bottom: 24px; }
.mb-3 { margin-bottom: 16px; }

.card { background: #fff; border: 1px solid #e2e4ec; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }
.config-panel-sheet .card {
  background: #f8fafc;
  border-color: #e8ecf0;
  box-shadow: none;
}
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
.align-start { align-items: start; }
.col-left { display: flex; flex-direction: column; }
.col-right { display: flex; flex-direction: column; }

h4 { margin: 0 0 16px 0; font-size: 15px; color: #1a1d2e; }
h5 { margin: 0 0 8px 0; font-size: 14px; color: #1a1d2e; }
.text-bold { font-weight: bold; }
.desc { font-size: 12px; color: #6b7280; margin: 0; line-height: 1.5; }
.flex-center { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
.text-blue { color: #1A6AFF; margin: 8px 0; font-size: 28px; font-weight: bold; }
.badge { background: #d1fae5; color: #059669; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }

.field-hint { font-size: 12px; color: #6b7280; line-height: 1.55; margin: 0 0 10px 0; }
.field-hint strong { color: #4b5563; font-weight: 600; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 13px; color: #4b5563; margin-bottom: 8px; font-weight: 500; }
.form-group input[type="text"], .form-group input[type="number"], select { width: 100%; height: 40px; padding: 0 10px; border: 1px solid #e2e4ec; border-radius: 6px; outline: none; font-size: 14px; box-sizing: border-box;}
.form-group input:focus, select:focus { border-color: #1A6AFF; }
.form-group :deep(.filter-select-root) { width: 100%; }
.form-group :deep(.filter-select-trigger) {
  width: 100%;
  padding: 10px 36px 10px 10px;
  border-radius: 6px;
  border-color: #e2e4ec;
}
.form-group :deep(.filter-select-trigger:focus) {
  border-color: #1a6aff;
  box-shadow: 0 0 0 3px rgba(26, 106, 255, 0.12);
}
.input-with-unit { display: flex; align-items: center; background: #fff; border: 1px solid #e2e4ec; border-radius: 6px; overflow: hidden; }
.input-with-unit input { border: none; flex: 1; border-radius: 0; }
.input-with-unit span { padding: 0 12px; background: #f9fafb; color: #6b7280; font-size: 13px; border-left: 1px solid #e2e4ec; height: 100%; display: flex; align-items: center;}

.form-row { display: flex; justify-content: space-between; align-items: center; }
.form-row label { font-size: 13px; color: #1a1d2e; font-weight: 500; }
.form-row small { display: block; font-size: 12px; color: #9ca3af; font-weight: normal; margin-top: 4px; }

.toggle { width: 40px; height: 24px; background: #d1d5db; border-radius: 12px; position: relative; cursor: pointer; flex-shrink:0;}
.toggle.on { background: #1A6AFF; }
.toggle::after { content: ''; position: absolute; width: 18px; height: 18px; background: white; border-radius: 50%; top: 3px; left: 3px; transition: 0.2s; }
.toggle.on::after { left: 19px; }

.color-row { display: flex; align-items: center; margin-bottom: 10px; padding: 8px; background: #f9fafb; border-radius: 6px; }
.color-box { width: 24px; height: 24px; border-radius: 4px; margin-right: 12px; }
.color-name { flex: 1; font-size: 13px; color: #1a1d2e; }
.color-hex { color: #6b7280; font-size: 13px; font-family: monospace; margin-right: 12px; }
.btn-del { background: none; border: none; color: #9ca3af; cursor: pointer; }
.btn-del:hover { color: #ef4444; }
.btn-add { text-align: center; height: 36px; display: flex; align-items: center; justify-content: center; padding: 0 12px; border: 1px dashed #d1d5db; border-radius: 6px; color: #6b7280; font-size: 13px; cursor: pointer; box-sizing: border-box; }
.btn-add:hover { border-color: #1A6AFF; color: #1A6AFF; }

.tags { display: flex; gap: 8px; flex-wrap: wrap; }
.tag { background: #f0f4ff; color: #1A6AFF; padding: 4px 10px; border-radius: 6px; font-size: 12px; border: 1px solid #dbeafe; display:flex; align-items:center;}
.tag-rm { cursor: pointer; margin-left: 6px; color: #9ca3af;}
.tag-rm:hover { color: #ef4444;}
.tag-add { border: 1px dashed #d1d5db; color: #6b7280; padding: 4px 10px; border-radius: 6px; font-size: 12px; cursor: pointer; background: white;}
.tag-add:hover { border-color: #1A6AFF; color: #1A6AFF; }

.btn-primary { background: #1A6AFF; color: white; border: none; height: 40px; padding: 0 24px; border-radius: 20px; font-size: 14px; cursor: pointer; font-weight: bold; display: inline-flex; align-items: center; justify-content: center; box-sizing: border-box; }
.btn-primary:disabled { opacity: 0.45; cursor: not-allowed; }
.btn-ghost { background: white; color: #4b5563; border: 1px solid #d1d5db; height: 40px; padding: 0 24px; border-radius: 20px; font-size: 14px; cursor: pointer; margin-right: 12px; display: inline-flex; align-items: center; justify-content: center; box-sizing: border-box; }

.footer-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 0;
}
/* 规范管理：取消 / 保存 吸底（相对主内容区与卡片左右对齐） */
.config-panel-sheet .footer-actions.config-footer-dock {
  position: fixed;
  bottom: 0;
  left: calc(260px + max(0px, (100vw - 1440px) / 2) + 20px);
  width: calc(min(100vw, 1440px) - 260px - 40px);
  max-width: calc(100vw - 260px - 40px);
  box-sizing: border-box;
  margin-top: 0;
  padding: 14px 28px calc(14px + env(safe-area-inset-bottom, 0px));
  border-radius: 12px 12px 0 0;
  background: rgba(250, 251, 252, 0.96);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-top: 1px solid #f0f1f5;
  border-left: 1px solid #e8eaef;
  border-right: 1px solid #e8eaef;
  box-shadow: 0 -2px 12px rgba(15, 23, 42, 0.05);
  z-index: 200;
}
.upload-area { border: 2px dashed #d1d5db; padding: 40px 20px; text-align: center; border-radius: 12px; background: #f9fafb; cursor: pointer; }
.upload-icon { font-size: 32px; color: #9ca3af; margin-bottom: 10px; }
.upload-area a { color: #1A6AFF; text-decoration: none; }
.w-100 { width: 100%; }
.flex { display: flex; }
.gap-2 { gap: 10px; }

/* Component Mode Styles */
.color-card { border: 1px solid #e2e4ec; border-radius: 8px; overflow: hidden; background: white; }
.color-block { height: 60px; width: 100%; }
.color-info { padding: 12px; }
.color-info strong { display: block; font-size: 14px; margin-bottom: 4px; color: #1a1d2e; }
.color-info .hex { font-family: monospace; color: #6b7280; font-size: 13px; }
.color-info .color-desc { font-size: 12px; color: #9ca3af; margin-top: 6px; line-height: 1.4; }

.color-row-item { display: flex; align-items: center; padding: 12px; border: 1px solid #e2e4ec; border-radius: 8px; background: white; }
.color-row-item .color-box { width: 32px; height: 32px; border-radius: 6px; margin-right: 12px; border: 1px solid rgba(0,0,0,0.05); }

.grid-6 { display: grid; grid-template-columns: repeat(6, 1fr); gap: 16px; }

/* 精度设置网格 */
.precision-tabs { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
.precision-opt { border: 2px solid #e2e4ec; border-radius: 12px; padding: 18px; cursor: pointer; display: flex; gap: 14px; transition: all 0.2s;}
.precision-opt.active { border-color: #1A6AFF; background: #f0f4ff; }
.precision-radio { width: 18px; height: 18px; border-radius: 50%; border: 2px solid #c8cad4; flex-shrink: 0; margin-top: 2px; }
.precision-opt.active .precision-radio { border-color: #1A6AFF; background: #1A6AFF; box-shadow: inset 0 0 0 3px white; }
.precision-opt-name { font-size: 15px; font-weight: 700; color: #1a1d2e; margin-bottom: 4px;}
.precision-opt-desc { font-size: 12px; color: #6b7280; }

.ignore-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.check-group-title { font-size: 14px; font-weight: 700; color: #4b5563; margin-bottom: 12px; }
.checkbox-item { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #1a1d2e; margin-bottom: 10px; cursor: pointer;}
.checkbox-item input { width: 16px; height: 16px; accent-color: #1A6AFF;}

.anchor-grid { display: grid; grid-template-columns: repeat(3, 36px); grid-template-rows: repeat(3, 36px); gap: 6px; }
.anchor-dot { width: 36px; height: 36px; border: 2px solid #d1d5db; border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center; background:#fafbfd; transition: all 0.2s;}
.anchor-dot.active { background: #1A6AFF; border-color: #1A6AFF; }
.anchor-dot.active::after { content: ''; width: 8px; height: 8px; background: white; border-radius: 50%; }

/* Component mode specific */
.comp-desc { font-size: 13px; color: #6b7280; margin: 0 0 20px 0; line-height: 1.6; }
.section-num { color: #1A6AFF; margin-right: 6px; }
.sub-item.active { color: #1A6AFF; font-weight: bold; }

.text-color-row { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #f3f4f6; }
.text-color-row:last-child { border-bottom: none; }
.color-box-sm { width: 20px; height: 20px; border-radius: 4px; border: 1px solid rgba(0,0,0,0.08); flex-shrink: 0; }
.tc-key { font-size: 12px; color: #6b7280; flex: 1; }
.tc-val { font-family: monospace; font-size: 12px; color: #1a1d2e; }

.spacing-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.spacing-label { font-size: 12px; font-family: monospace; color: #1A6AFF; width: 36px; flex-shrink: 0; }
.spacing-bar { height: 10px; background: #1A6AFF; border-radius: 2px; min-width: 4px; max-width: 120px; }
.spacing-name { font-size: 12px; color: #6b7280; }

.comp-badge { display: inline-block; background: #f0f4ff; color: #1A6AFF; border: 1px solid #dbeafe; border-radius: 6px; padding: 2px 10px; font-size: 13px; font-weight: 600; }

/* Button demos */
.btn-states { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 8px; }
.demo-btn { padding: 0 16px; height: 32px; border-radius: 4px; font-size: 13px; cursor: default; }
.demo-btn.primary { background: #1A6AFF; color: white; border: none; }
.demo-btn.primary.hover { background: #256AF4; }
.demo-btn.primary.active { background: #145BD7; }
.demo-btn.primary.disabled { background: #A3C3FF; cursor: not-allowed; }
.demo-btn.secondary { background: #F0F4FF; color: #1A6AFF; border: 1px solid #dbeafe; }
.demo-btn.secondary.hover { background: #EAF0FF; }
.demo-btn.secondary.active-s { background: #EFF1F7; }
.demo-btn.secondary.disabled { background: #F5F7FA; color: #9ca3af; cursor: not-allowed; }
.demo-btn.dashed { background: white; color: #4b5563; border: 1px dashed #d1d5db; }
.demo-btn.dashed.disabled { color: #9ca3af; cursor: not-allowed; }
.demo-text-btn { font-size: 13px; color: #1A6AFF; cursor: default; padding: 4px 8px; }
.demo-text-btn.hover { color: #256AF4; }
.demo-text-btn.active-s { color: #145BD7; }
.demo-text-btn.disabled { color: #9ca3af; }

.btn-state-values { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }
.bsv { display: flex; align-items: center; gap: 4px; font-size: 11px; color: #4b5563; }
.bsv-dot { width: 12px; height: 12px; border-radius: 3px; flex-shrink: 0; border: 1px solid rgba(0,0,0,0.06); }

/* Input demos */
.state-color-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
.scg-item { display: flex; flex-direction: column; gap: 4px; }
.scg-label { font-size: 11px; color: #6b7280; }
.demo-input { padding: 6px 10px; border-radius: 4px; font-size: 12px; }
.demo-input.normal { border: 1px solid #C0C0E3; }
.demo-input.focus { border: 1px solid #1A6AFF; }
.demo-input.error { border: 1px solid #F97F7F; }
.demo-input.disabled-i { border: 1px solid #e2e4ec; background: #F5F7F9; color: #9ca3af; }

/* Radio/Checkbox demos */
.demo-radio { width: 16px; height: 16px; border-radius: 50%; }
.demo-radio.uncheck { border: 2px solid #C0C0E3; }
.demo-radio.checked { border: 4px solid #1A6AFF; }
.demo-radio.disabled-r { border: 2px solid #e2e4ec; background: #F5F7F9; }
.demo-checkbox { width: 16px; height: 16px; border-radius: 3px; }
.demo-checkbox.uncheck { border: 2px solid #C0C0E3; }
.demo-checkbox.checked { background: #1A6AFF; border: 2px solid #1A6AFF; }
.demo-checkbox.disabled-c { border: 2px solid #e2e4ec; background: #F5F7F9; }

</style>
