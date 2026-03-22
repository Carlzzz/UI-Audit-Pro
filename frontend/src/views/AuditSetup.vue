<template>
  <div class="page-container">
    <AppNavbar variant="full" active-key="scan" />
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
      <div class="sidebar" style="display:none;">
        <div class="sidebar-title">规范管理</div>
        <div class="nav-item" :class="{active: activeTab === 'baseline'}" @click="activeTab = 'baseline'">
           <span class="icon" aria-hidden="true"><IconStroke name="baseline" size="sm" /></span> 基准值模式
        </div>
        <div class="nav-group">
          <div class="nav-item group-title" :class="{active: activeTab === 'component'}" @click="activeTab = 'component'; expandComponents = !expandComponents">
            <span class="icon" aria-hidden="true"><IconStroke name="component" size="sm" /></span> 组件模式
            <span class="arrow" aria-hidden="true"><IconStroke name="chevron-down" size="sm" class="nav-chevron" :class="{ open: expandComponents }" /></span>
          </div>
          <div class="sub-nav" v-show="expandComponents && activeTab === 'component'">
            <div class="sub-item">全局基础规范</div>
            <div class="sub-item">按钮组件</div>
            <div class="sub-item">数据录入类组件</div>
            <div class="sub-item">数据展示与导航组件</div>
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
          <div>
            <div class="breadcrumb">新建走查 <span class="sep">/</span> <span class="cur">{{ activeTab === 'baseline' ? '基准值模式' : (activeTab.startsWith('comp_') ? '组件模式' : '设计稿模式') }}</span></div>
            <h2>{{ activeTab === 'baseline' ? '基准值模式' : (activeTab.startsWith('comp_') ? '组件模式' : '设计稿模式') }}</h2>
            <p class="subtitle">定义设计走查的全局基准规范或接入设计资源</p>
          </div>
          <div class="toggle-group-top" @click="activeTab === 'baseline' ? baselineConfig.globalEnable = !baselineConfig.globalEnable : (activeTab.startsWith('comp_') ? componentConfig.globalEnable = !componentConfig.globalEnable : designConfig.globalEnable = !designConfig.globalEnable)">
             <span style="font-size:14px; font-weight:bold; color:#1a1d2e; margin-right:8px;">一键开启</span>
             <div class="toggle" :class="{on: activeTab === 'baseline' ? baselineConfig.globalEnable : (activeTab.startsWith('comp_') ? componentConfig.globalEnable : designConfig.globalEnable)}"></div>
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
                <select v-model="baselineConfig.textOverflow"><option>默认使用省略号</option><option>换行显示</option></select>
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

          <!-- 5. 鉴权与登录状态 (新增强大特性) -->
          <div class="section-title mt-4"><span class="icon blue">🔑</span> 5. 页面鉴权与登录状态</div>
          <div class="card">
             <p class="desc mb-3">如果走查的目标页面需要登录后才能访问，请在此处提供认证信息 (三选一即可)：</p>
             <div class="grid-2 mb-3">
               <div class="form-group">
                 <label>自动登录账号</label>
                 <input type="text" v-model="baselineConfig.loginUser" placeholder="例如: admin" />
               </div>
               <div class="form-group">
                 <label>自动登录密码</label>
                 <input type="password" v-model="baselineConfig.loginPwd" placeholder="例如: 123456" style="width: 100%; padding: 10px; border: 1px solid #e2e4ec; border-radius: 8px;" />
               </div>
             </div>
             <div class="grid-2" style="border-top: 1px dashed #e8eaf0; padding-top: 16px;">
               <div class="form-group">
                 <label>请求头 Cookie</label>
                 <input type="text" v-model="baselineConfig.cookieStr" placeholder="例如: session_id=123456789; token=abc..." />
                 <small style="color:#9ca3af; font-size: 12px; margin-top:4px; display:block;">推荐！免除验证码烦恼</small>
               </div>
               <div class="form-group">
                 <label>LocalStorage 注入 (JSON 格式)</label>
                 <input type="text" v-model="baselineConfig.localStorageStr" placeholder='例如: {"Access-Token": "Bearer xxxx"}' />
                 <small style="color:#9ca3af; font-size: 12px; margin-top:4px; display:block;">用于前端依赖本地缓存渲染的单页应用</small>
               </div>
             </div>
          </div>
        </div>

        <div v-if="activeTab.startsWith('comp_')" class="form-container">
          <div class="section-title"><span class="icon blue">品</span> 组件模式规范定义</div>
          <p class="desc mb-4" style="color:#ef4444; font-weight:bold;">提示：组件模式的参数非常多，请先前往“规范管理”页面完成全局和各个组件参数的精细化配置。这里的开关用于快速开启或关闭特定组件的走查项。</p>
          <div class="grid-2">
            <div class="card mb-4">
              <h4>🔘 按钮组件检测</h4>
              <div class="form-row mt-3" @click="componentConfig.checkButtonState = !componentConfig.checkButtonState">
                 <label>开启按钮规范与状态检测</label>
                 <div class="toggle" :class="{on: componentConfig.checkButtonState}"></div>
              </div>
            </div>
            
            <div class="card mb-4">
              <h4>⌨️ 数据录入类组件检测</h4>
              <div class="form-row mt-3" @click="componentConfig.checkInputState = !componentConfig.checkInputState">
                 <label>开启输入框规范检测</label>
                 <div class="toggle" :class="{on: componentConfig.checkInputState}"></div>
              </div>
            </div>
            
            <div class="card mb-4">
              <h4>📊 数据展示组件检测</h4>
              <div class="form-row mt-3" @click="componentConfig.checkTableAlignment = !componentConfig.checkTableAlignment">
                 <label>开启表格行高及对齐检测</label>
                 <div class="toggle" :class="{on: componentConfig.checkTableAlignment}"></div>
              </div>
            </div>
            
            <div class="card mb-4">
              <h4>🧭 导航组件检测</h4>
              <div class="form-row mt-3" @click="componentConfig.checkFormSpacing = !componentConfig.checkFormSpacing">
                 <label>开启导航栏高度与间距检测</label>
                 <div class="toggle" :class="{on: componentConfig.checkFormSpacing}"></div>
              </div>
            </div>
          </div>
          
          <div class="section-title mt-4"><span class="icon blue">🔑</span> 页面鉴权与登录状态</div>
          <div class="card mb-4">
             <p class="desc mb-3">如果走查的目标页面需要登录后才能访问，请在此处提供认证信息 (三选一即可)：</p>
             <div class="grid-2 mb-3">
               <div class="form-group">
                 <label>自动登录账号</label>
                 <input type="text" v-model="componentConfig.loginUser" placeholder="例如: admin" />
               </div>
               <div class="form-group">
                 <label>自动登录密码</label>
                 <input type="password" v-model="componentConfig.loginPwd" placeholder="例如: 123456" style="width: 100%; padding: 10px; border: 1px solid #e2e4ec; border-radius: 8px;" />
               </div>
             </div>
             <div class="grid-2" style="border-top: 1px dashed #e8eaf0; padding-top: 16px;">
               <div class="form-group">
                 <label>请求头 Cookie</label>
                 <input type="text" v-model="componentConfig.cookieStr" placeholder="例如: session_id=123..." />
               </div>
               <div class="form-group">
                 <label>LocalStorage 注入 (JSON)</label>
                 <input type="text" v-model="componentConfig.localStorageStr" placeholder='{"token": "xxx"}' />
               </div>
             </div>
          </div>
        </div>

        <div v-if="activeTab === 'design'" class="form-container">
          <!-- 设计稿模式特有配置 -->

          <div class="section-title"><span class="icon blue">🗂</span> 设计资源接入</div>
          <div class="card mb-4">
            <div
              class="upload-zone"
              :class="{ 'upload-zone--dragover': isDragging, 'upload-zone--has-file': designConfig.uploadedFile }"
              @dragover.prevent="isDragging = true"
              @dragleave.prevent="isDragging = false"
              @drop.prevent="onFileDrop"
              @click="$refs.fileInput.click()"
            >
              <input
                ref="fileInput"
                type="file"
                accept=".png,.jpg,.jpeg,.svg,.pdf,.html"
                style="display:none"
                @change="onFileChange"
              />
              <template v-if="!designConfig.uploadedFile">
                <div class="upload-icon">⬆</div>
                <div class="upload-hint">拖拽文件至此，或 <span class="upload-link">点击选择</span></div>
                <div class="upload-formats">支持格式：PNG、JPG、SVG、PDF、HTML</div>
              </template>
              <template v-else>
                <div class="upload-preview">
                  <img
                    v-if="designConfig.uploadedFile.file_type === 'image' || designConfig.uploadedFile.preview_url"
                    :src="`http://localhost:8000${designConfig.uploadedFile.preview_url || designConfig.uploadedFile.file_url}`"
                    class="preview-img"
                    alt="preview"
                  />
                  <div v-else class="preview-icon">
                    <span v-if="designConfig.uploadedFile.file_type === 'pdf'">📄</span>
                    <span v-else-if="designConfig.uploadedFile.file_type === 'html'">🌐</span>
                    <span v-else>📁</span>
                  </div>
                  <div class="preview-info">
                    <div class="preview-name">{{ designConfig.uploadedFile.file_name }}</div>
                    <div class="preview-type">{{ designConfig.uploadedFile.file_type.toUpperCase() }}</div>
                  </div>
                  <button class="preview-remove" @click.stop="removeUploadedFile">✕</button>
                </div>
              </template>
            </div>
            <div v-if="uploadError" class="upload-error">{{ uploadError }}</div>
            <div v-if="uploading" class="upload-status">上传中...</div>
          </div>
        
          
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
          
          <!-- 鉴权部分同样加给设计稿模式 -->
          <div class="section-title mt-4"><span class="icon blue">🔑</span> 页面鉴权与登录状态</div>
          <div class="card mb-4">
             <p class="desc mb-3">如果走查的目标页面需要登录后才能访问，请在此处提供认证信息 (三选一即可)：</p>
             <div class="grid-2 mb-3">
               <div class="form-group">
                 <label>自动登录账号</label>
                 <input type="text" v-model="designConfig.loginUser" placeholder="例如: admin" />
               </div>
               <div class="form-group">
                 <label>自动登录密码</label>
                 <input type="password" v-model="designConfig.loginPwd" placeholder="例如: 123456" style="width: 100%; padding: 10px; border: 1px solid #e2e4ec; border-radius: 8px;" />
               </div>
             </div>
             <div class="grid-2" style="border-top: 1px dashed #e8eaf0; padding-top: 16px;">
               <div class="form-group">
                 <label>请求头 Cookie</label>
                 <input type="text" v-model="designConfig.cookieStr" placeholder="例如: session_id=123..." />
               </div>
               <div class="form-group">
                 <label>LocalStorage 注入 (JSON)</label>
                 <input type="text" v-model="designConfig.localStorageStr" placeholder='{"token": "xxx"}' />
               </div>
             </div>
          </div>
        </div>

        </div>

        <div class="footer-actions footer-actions--fixed" aria-label="走查操作">
          <div class="footer-actions-inner">
            <button type="button" class="btn-ghost" @click="$router.push('/')">取消</button>
            <button type="button" class="btn-ghost btn-save-session" title="仅保存在本页会话内存，不会写入「规范管理」" @click="saveSessionDraft">保存</button>
            <button type="button" class="btn-primary btn-primary-with-icon" @click="startScan">
              <IconStroke name="bolt" size="sm" strokeWeight="2" class="btn-primary-icon" />
              开启走查
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuditStore } from '../store/audit'
import { useUserStore } from '../store/user'
import AppNavbar from '../components/AppNavbar.vue'
import IconStroke from '../components/IconStroke.vue'
import SpecAddFloat from '../components/SpecAddFloat.vue'
import SpecColorFloat from '../components/SpecColorFloat.vue'
import axios from 'axios'
import { openSpecAddPanel, confirmSpecAddPanel, openColorEditPanel } from '../utils/specModal'
import { showToastInfo, showToastSuccess } from '../utils/modal'
import { normalizeResponsiveBreakpoints } from '../utils/baselineConfig'
import { normalizeAsciiPunctuation } from '../utils/punctuationNormalize'

const router = useRouter()
const auditStore = useAuditStore()
const userStore = useUserStore()

const activeTab = ref(auditStore.checkMode === 'component' ? 'comp_global' : (auditStore.checkMode || 'baseline'))
const expandComponents = ref(true)
const isDragging = ref(false)
const uploading = ref(false)
const uploadError = ref('')

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
  globalEnable: true,
  cookieStr: '',
  localStorageStr: '',
  loginUser: '',
  loginPwd: ''
}

const defaultDesign = {
  globalEnable: true,
  url: '',
  compareWidth: 1440,
  deviceType: '桌面端',
  colorThreshold: 10,
  aiAnalysis: true,
  aiSummary: true,
  precisionMode: 'pixel',
  ignoreStatus: true,
  ignoreAds: false,
  anchor: 0,
  cookieStr: '',
  localStorageStr: '',
  loginUser: '',
  loginPwd: ''
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
  },
  // Feature flags for audit checks
  checkButtonState: true,
  checkInputState: true,
  checkTableAlignment: true,
  checkFormSpacing: true,
  cookieStr: '',
  localStorageStr: '',
  loginUser: '',
  loginPwd: ''
}

// 初始化配置为空
const baselineConfig = reactive(JSON.parse(JSON.stringify(defaultBaseline)))
const designConfig = reactive(JSON.parse(JSON.stringify(defaultDesign)))
const componentConfig = reactive(JSON.parse(JSON.stringify(defaultComponent)))

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
  setTimeout(() => {
    watch(baselineConfig, () => {
      isDirty.value = true
      auditStore.clearSessionDraft('baseline')
    }, { deep: true })
    watch(componentConfig, () => {
      isDirty.value = true
      auditStore.clearSessionDraft('component')
    }, { deep: true })
    watch(designConfig, () => {
      isDirty.value = true
      auditStore.clearSessionDraft('design')
    }, { deep: true })
  }, 100)
})

/** 列表类文本失焦：全角标点转半角，避免中文输入法下的「，」「、」导致解析与走查不一致 */
const normBaselineListFields = () => {
  ;['transitions', 'fontFamily', 'fontSizes', 'lineHeights', 'fontWeights'].forEach((k) => {
    if (baselineConfig[k] != null && baselineConfig[k] !== '') {
      baselineConfig[k] = normalizeAsciiPunctuation(baselineConfig[k])
    }
  })
}

const normComponentTypographyFields = () => {
  const t = componentConfig.typography
  if (!t || typeof t !== 'object') return
  ;['family', 'sizes', 'lineHeights', 'weights'].forEach((k) => {
    if (t[k] != null && t[k] !== '') t[k] = normalizeAsciiPunctuation(t[k])
  })
}

/**
 * 仅作用于深拷贝后的纯对象，不触碰页面上的 reactive 配置。
 * 若在「保存 / 构建走查配置」里原地改 baselineConfig，会触发 watch → clearSessionDraft，
 * 可能在 setSessionDraft 之后清空会话快照，导致开启走查仍用旧逻辑或 draft 丢失。
 */
const normalizeBaselineStringsOnPlain = (obj) => {
  if (!obj || typeof obj !== 'object') return
  ;['transitions', 'fontFamily', 'fontSizes', 'lineHeights', 'fontWeights'].forEach((k) => {
    if (obj[k] != null && obj[k] !== '') obj[k] = normalizeAsciiPunctuation(obj[k])
  })
}

const normalizeComponentTypographyOnPlain = (obj) => {
  const t = obj?.typography
  if (!t || typeof t !== 'object') return
  ;['family', 'sizes', 'lineHeights', 'weights'].forEach((k) => {
    if (t[k] != null && t[k] !== '') t[k] = normalizeAsciiPunctuation(t[k])
  })
}

/** 与开启走查、保存会话共用：当前 Tab 对应的模式键 */
const getSessionModeKey = () => {
  if (activeTab.value === 'baseline') return 'baseline'
  if (activeTab.value.startsWith('comp_')) return 'component'
  return 'design'
}

/** 序列化当前表单为本次走查配置（深拷贝；不修改 reactive，避免 watch 清空 sessionDraft） */
const buildConfigSnapshotForScan = () => {
  if (activeTab.value === 'baseline') {
    const snap = JSON.parse(JSON.stringify(baselineConfig))
    normalizeBaselineStringsOnPlain(snap)
    return snap
  }
  if (activeTab.value.startsWith('comp_')) {
    const snap = JSON.parse(JSON.stringify(componentConfig))
    normalizeComponentTypographyOnPlain(snap)
    return snap
  }
  return JSON.parse(JSON.stringify(designConfig))
}

/** 保存到会话内存：不写规则管理 API；开启走查将优先使用此次快照（改表单后会自动作废） */
const saveSessionDraft = () => {
  const modeKey = getSessionModeKey()
  const snap = buildConfigSnapshotForScan()
  auditStore.setSessionDraft(modeKey, snap)
  showToastSuccess('已保存到本次走查会话（未写入规范管理）')
}

const startScan = () => {
  const modeKey = getSessionModeKey()
  const draft = auditStore.sessionDraft[modeKey]
  const cfg = draft != null ? JSON.parse(JSON.stringify(draft)) : buildConfigSnapshotForScan()
  auditStore.setTaskConfig(cfg)
  if (activeTab.value.startsWith('comp_')) {
    auditStore.setCheckMode('component')
  } else {
    auditStore.setCheckMode(activeTab.value)
  }
  router.push('/scan')
}

const addToken = (e, arr, val, title) => openSpecAddPanel(specFloat, e, arr, val, title || '添加规范值')

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

const uploadFile = async (file) => {
  const allowed = ['image/png', 'image/jpeg', 'image/svg+xml', 'application/pdf', 'text/html']
  if (!allowed.includes(file.type) && !file.name.match(/\.(png|jpg|jpeg|svg|pdf|html)$/i)) {
    uploadError.value = '不支持的文件格式，请上传 PNG、JPG、SVG、PDF 或 HTML 文件'
    return
  }
  uploadError.value = ''
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await axios.post('http://localhost:8000/api/design/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    if (res.data.status === 'success') {
      designConfig.uploadedFile = res.data.data
    } else {
      uploadError.value = res.data.detail || '上传失败'
    }
  } catch (e) {
    uploadError.value = e.response?.data?.detail || '上传失败，请检查后端服务'
  } finally {
    uploading.value = false
  }
}

const onFileChange = (e) => {
  const file = e.target.files[0]
  if (file) uploadFile(file)
}

const onFileDrop = (e) => {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file) uploadFile(file)
}

const removeUploadedFile = () => {
  designConfig.uploadedFile = null
  uploadError.value = ''
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
.page-container {
  min-height: 100vh;
  padding-top: 60px;
  padding-bottom: calc(56px + env(safe-area-inset-bottom, 0px));
  box-sizing: border-box;
  position: relative;
  /* 第四张图风格背景：图片底座 + CSS 渐变叠加实现高清过渡，避免位图缩放模糊 */
  background-color: #f0f4ff;
  background-image:
    radial-gradient(ellipse 70% 50% at 50% 45%, rgba(255, 255, 255, 0.65) 0%, transparent 58%),
    radial-gradient(ellipse 40% 30% at 90% 10%, rgba(226, 232, 255, 0.5) 0%, transparent 48%),
    radial-gradient(ellipse 45% 35% at 8% 92%, rgba(232, 238, 252, 0.45) 0%, transparent 50%),
    url('/images/audit-setup-bg.png');
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
}
.config-layout { display: flex; max-width: 1440px; margin: 0 auto; min-height: calc(100vh - 60px); }
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

.main-content {
  flex: 1;
  overflow: visible;
  display: flex;
  flex-direction: column;
  background: transparent;
  padding: 16px 20px 0;
  box-sizing: border-box;
}

.config-panel-sheet {
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(15, 23, 42, 0.06);
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.config-panel-sheet .content-header {
  padding: 22px 28px 18px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid rgba(240, 241, 245, 0.8);
}
.content-header { padding: 30px 40px 10px; display: flex; justify-content: space-between; align-items: flex-start; }
.form-container { padding: 0 40px; flex: 1; }
.config-panel-sheet .form-container { padding: 20px 28px 30px; flex: 0 0 auto; }

.breadcrumb { font-size: 13px; color: #9ca3af; margin-bottom: 8px; }
.breadcrumb .cur { color: #1a1d2e; font-weight: bold; }
h2 { margin: 0; font-size: 24px; color: #1a1d2e; }
.subtitle { margin: 6px 0 0 0; color: #6b7280; font-size: 14px; }

.toggle-group-top {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  padding: 6px 12px;
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
  cursor: pointer;
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

.card {
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 8px 28px rgba(15, 23, 42, 0.05);
}
.config-panel-sheet .card {
  background: rgba(255, 255, 255, 0.6);
  border-color: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
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
.form-group input[type="text"], .form-group input[type="number"], select { width: 100%; height: 40px; padding: 0 10px; border: 1px solid #e2e4ec; border-radius: 8px; outline: none; font-size: 14px; box-sizing: border-box;}
.form-group input:focus, select:focus { border-color: #1A6AFF; }
.input-with-unit { display: flex; align-items: center; background: #fff; border: 1px solid #e2e4ec; border-radius: 8px; overflow: hidden; }
.input-with-unit input { border: none; flex: 1; border-radius: 0; }
.input-with-unit span { padding: 0 12px; background: #f9fafb; color: #6b7280; font-size: 13px; border-left: 1px solid #e2e4ec; height: 100%; display: flex; align-items: center;}

.form-row { display: flex; justify-content: space-between; align-items: center; }
.form-row label { font-size: 13px; color: #1a1d2e; font-weight: 500; }
.form-row small { display: block; font-size: 12px; color: #9ca3af; font-weight: normal; margin-top: 4px; }

.toggle { width: 40px; height: 24px; background: #d1d5db; border-radius: 12px; position: relative; cursor: pointer; flex-shrink:0;}
.toggle.on { background: #1A6AFF; }
.toggle::after { content: ''; position: absolute; width: 18px; height: 18px; background: white; border-radius: 50%; top: 3px; left: 3px; transition: 0.2s; }
.toggle.on::after { left: 19px; }

.color-row { display: flex; align-items: center; margin-bottom: 10px; padding: 8px; background: rgba(249, 250, 251, 0.8); border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.4); }
.color-box { width: 24px; height: 24px; border-radius: 4px; margin-right: 12px; }
.color-name { flex: 1; font-size: 13px; color: #1a1d2e; }
.color-hex { color: #6b7280; font-size: 13px; font-family: monospace; margin-right: 12px; }
.btn-del { background: none; border: none; color: #9ca3af; cursor: pointer; }
.btn-del:hover { color: #ef4444; }
.btn-add { text-align: center; height: 36px; display: flex; align-items: center; justify-content: center; padding: 0 12px; border: 1px dashed rgba(209, 213, 219, 0.9); border-radius: 12px; color: #6b7280; font-size: 13px; cursor: pointer; background: rgba(255, 255, 255, 0.6); box-sizing: border-box; }
.btn-add:hover { border-color: #1A6AFF; color: #1A6AFF; }

.tags { display: flex; gap: 8px; flex-wrap: wrap; }
.tag { background: #f0f4ff; color: #1A6AFF; padding: 4px 10px; border-radius: 8px; font-size: 12px; border: 1px solid #dbeafe; display:flex; align-items:center;}
.tag-rm { cursor: pointer; margin-left: 6px; color: #9ca3af;}
.tag-rm:hover { color: #ef4444;}
.tag-add { border: 1px dashed rgba(209, 213, 219, 0.9); color: #6b7280; padding: 4px 10px; border-radius: 10px; font-size: 12px; cursor: pointer; background: rgba(255, 255, 255, 0.7);}
.tag-add:hover { border-color: #1A6AFF; color: #1A6AFF; }

.btn-primary { background: #1A6AFF; color: white; border: none; height: 40px; padding: 0 24px; border-radius: 20px; font-size: 14px; cursor: pointer; font-weight: bold; display: inline-flex; align-items: center; justify-content: center; box-sizing: border-box; }
.btn-primary-with-icon { display: inline-flex; align-items: center; gap: 6px; }
.btn-primary-icon { flex-shrink: 0; }
.btn-ghost { background: white; color: #4b5563; border: 1px solid #d1d5db; height: 40px; padding: 0 24px; border-radius: 20px; font-size: 14px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; box-sizing: border-box; }
.btn-save-session { border-color: #c7d2fe; color: #1A6AFF; font-weight: 600; }
.btn-save-session:hover { background: #f5f7ff; border-color: #1A6AFF; }

.footer-actions.footer-actions--fixed {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  margin: 0;
  z-index: 100;
  padding: 12px 20px calc(12px + env(safe-area-inset-bottom, 0px));
  background: rgba(250, 251, 252, 0.98);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-top: 1px solid #f0f1f5;
  box-shadow: 0 -2px 10px rgba(15, 23, 42, 0.05);
}
.footer-actions-inner {
  max-width: 1440px;
  margin: 0 auto;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
}
.w-100 { width: 100%; }
.flex { display: flex; }
.gap-2 { gap: 10px; }

/* Upload Zone */
.upload-zone {
  border: 2px dashed rgba(200, 208, 224, 0.9);
  border-radius: 20px;
  padding: 36px 24px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  background: rgba(255, 255, 255, 0.55);
  backdrop-filter: blur(8px);
}
.upload-zone:hover, .upload-zone--dragover {
  border-color: #1A6AFF;
  background: rgba(234, 242, 255, 0.8);
}
.upload-zone--has-file {
  border-style: solid;
  border-color: #1A6AFF;
  background: rgba(240, 245, 255, 0.9);
  padding: 20px 24px;
}
.upload-icon { font-size: 28px; margin-bottom: 8px; color: #8a94a8; }
.upload-hint { font-size: 14px; color: #4b5563; margin-bottom: 4px; }
.upload-link { color: #1A6AFF; text-decoration: underline; }
.upload-formats { font-size: 12px; color: #9D9EA9; }
.upload-error { color: #e53e3e; font-size: 13px; margin-top: 8px; }
.upload-status { color: #1A6AFF; font-size: 13px; margin-top: 8px; }
.upload-preview { display: flex; align-items: center; gap: 16px; text-align: left; }
.preview-img { width: 80px; height: 60px; object-fit: cover; border-radius: 8px; border: 1px solid #e8eaf0; flex-shrink: 0; }
.preview-icon { font-size: 40px; flex-shrink: 0; }
.preview-info { flex: 1; min-width: 0; }
.preview-name { font-size: 14px; font-weight: 600; color: #1F1F21; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.preview-type { font-size: 12px; color: #9D9EA9; margin-top: 2px; }
.preview-remove { background: none; border: none; color: #9D9EA9; font-size: 16px; cursor: pointer; padding: 4px 8px; border-radius: 4px; flex-shrink: 0; }
.preview-remove:hover { background: #f0f0f5; color: #e53e3e; }

/* 精度设置网格 */
.precision-tabs { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
.precision-opt {
  border: 2px solid rgba(226, 228, 236, 0.8);
  border-radius: 18px;
  padding: 18px;
  cursor: pointer;
  display: flex;
  gap: 14px;
  transition: all 0.2s;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(8px);
}
.precision-opt:hover { background: rgba(255, 255, 255, 0.7); }
.precision-opt.active { border-color: #1A6AFF; background: rgba(240, 244, 255, 0.85); }
.precision-radio { width: 18px; height: 18px; border-radius: 50%; border: 2px solid #c8cad4; flex-shrink: 0; margin-top: 2px; }
.precision-opt.active .precision-radio { border-color: #1A6AFF; background: #1A6AFF; box-shadow: inset 0 0 0 3px white; }
.precision-opt-name { font-size: 15px; font-weight: 700; color: #1a1d2e; margin-bottom: 4px;}
.precision-opt-desc { font-size: 12px; color: #6b7280; }

.ignore-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.check-group-title { font-size: 14px; font-weight: 700; color: #4b5563; margin-bottom: 12px; }
.checkbox-item { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #1a1d2e; margin-bottom: 10px; cursor: pointer;}
.checkbox-item input { width: 16px; height: 16px; accent-color: #1A6AFF;}

.anchor-grid { display: grid; grid-template-columns: repeat(3, 36px); grid-template-rows: repeat(3, 36px); gap: 6px; }
.anchor-dot { width: 36px; height: 36px; border: 2px solid #d1d5db; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; background:#fafbfd; transition: all 0.2s;}
.anchor-dot.active { background: #1A6AFF; border-color: #1A6AFF; }
.anchor-dot.active::after { content: ''; width: 8px; height: 8px; background: white; border-radius: 50%; }
</style>
