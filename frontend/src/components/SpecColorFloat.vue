<template>
  <Teleport to="body">
    <div
      v-show="open"
      ref="panelRef"
      class="spec-float-panel spec-color-float"
      :style="panelStyle"
      role="dialog"
      aria-modal="true"
      @click.stop
    >
      <div class="spec-float-title">{{ title }}</div>

      <div class="spec-float-field">
        <span class="spec-float-label">颜色名称</span>
        <input v-model="localLabel" type="text" class="spec-float-input spec-float-input--full" autocomplete="off" />
      </div>

      <div class="spec-float-field">
        <span class="spec-float-label">色值 (HEX)</span>
        <div class="spec-float-inputs spec-float-inputs--color">
          <input
            type="color"
            class="spec-color-picker"
            :value="normalizedHex"
            @input="onPickerInput"
          />
          <input
            :value="localHex"
            type="text"
            class="spec-float-input spec-float-input--grow spec-float-input--mono"
            autocomplete="off"
            spellcheck="false"
            @input="onHexTextInput"
          />
        </div>
      </div>

      <div class="spec-float-actions">
        <button type="button" class="spec-float-btn spec-float-btn--ghost" @click="close">取消</button>
        <button type="button" class="spec-float-btn spec-float-btn--primary" @click="submit">确认</button>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch, computed, onUnmounted, nextTick } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  left: { type: Number, default: 0 },
  top: { type: Number, default: 0 },
  title: { type: String, default: '修改色值' },
  initialLabel: { type: String, default: '' },
  initialHex: { type: String, default: '#000000' },
})

const emit = defineEmits(['update:open', 'confirm'])

const panelRef = ref(null)
const localLabel = ref('')
const localHex = ref('#000000')

const panelStyle = computed(() => ({
  left: `${props.left}px`,
  top: `${props.top}px`,
}))

const normalizedHex = computed(() => {
  let h = String(localHex.value || '').trim()
  if (!/^#[0-9A-Fa-f]{6}$/i.test(h)) return '#000000'
  return h.toUpperCase()
})

function onPickerInput(e) {
  localHex.value = String(e.target.value || '').toUpperCase()
}

function normalizeHexInput(raw) {
  let v = String(raw || '').trim()
  if (!v) return ''
  if (!v.startsWith('#')) {
    const alnum = v.replace(/[^0-9a-fA-F]/g, '').toUpperCase().slice(0, 6)
    return alnum ? `#${alnum}` : ''
  }
  const body = v.slice(1).replace(/[^0-9a-fA-F]/g, '').toUpperCase().slice(0, 6)
  if (!body) return '#'
  return `#${body}`
}

function onHexTextInput(e) {
  localHex.value = normalizeHexInput(e?.target?.value ?? '')
}

function syncFromProps() {
  localLabel.value = props.initialLabel || ''
  let h = String(props.initialHex || '#000000').trim()
  if (!/^#[0-9A-Fa-f]{6}$/i.test(h)) h = '#000000'
  localHex.value = h.toUpperCase()
}

function close() {
  emit('update:open', false)
}

function submit() {
  let hex = normalizeHexInput(localHex.value)
  if (!/^#[0-9A-F]{6}$/.test(hex)) {
    hex = normalizedHex.value
  }
  emit('confirm', { label: localLabel.value.trim(), hex })
  emit('update:open', false)
}

let offDoc = null
watch(
  () => props.open,
  async (o) => {
    if (offDoc) {
      document.removeEventListener('mousedown', offDoc)
      offDoc = null
    }
    if (o) {
      syncFromProps()
      await nextTick()
      offDoc = (e) => {
        if (panelRef.value && !panelRef.value.contains(e.target)) close()
      }
      setTimeout(() => document.addEventListener('mousedown', offDoc), 0)
    }
  }
)

watch(
  () => [props.initialLabel, props.initialHex],
  () => {
    if (props.open) syncFromProps()
  }
)

onUnmounted(() => {
  if (offDoc) document.removeEventListener('mousedown', offDoc)
})
</script>

<style scoped>
.spec-float-panel {
  position: fixed;
  z-index: 4000;
  min-width: 300px;
  max-width: min(360px, calc(100vw - 16px));
  padding: 14px 0 12px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(15, 23, 42, 0.12), 0 4px 12px rgba(15, 23, 42, 0.06);
}

.spec-float-title {
  font-size: 16px;
  font-weight: 700;
  color: #1a1d2e;
  padding: 0 20px 12px;
  text-align: left;
  line-height: 1.3;
}

.spec-float-field {
  padding: 0 20px 12px;
}

.spec-float-label {
  display: block;
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 8px;
}

.spec-float-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.spec-float-inputs--color {
  align-items: stretch;
}

.spec-float-input {
  height: 32px;
  padding: 0 10px;
  border: 1px solid #e2e4ec;
  border-radius: 8px;
  font-size: 14px;
  color: #1a1d2e;
  background: #fff;
  box-sizing: border-box;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.spec-float-input--full {
  width: 100%;
}

.spec-float-input--grow {
  flex: 1;
  min-width: 120px;
  width: auto;
}

.spec-float-input--mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

.spec-float-input:hover {
  border-color: #1a6aff;
}

.spec-float-input:focus {
  border-color: #1a6aff;
  box-shadow: 0 0 0 2px rgba(26, 106, 255, 0.15);
}

.spec-color-picker {
  width: 32px;
  height: 32px;
  padding: 0;
  border: 1px solid #e2e4ec;
  border-radius: 8px;
  cursor: pointer;
  flex-shrink: 0;
  background: none;
  overflow: hidden;
}

.spec-color-picker:hover {
  border-color: #1a6aff;
}

.spec-float-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 4px 20px 0;
  border-top: 1px solid #f0f1f5;
  margin-top: 4px;
  padding-top: 12px;
}

.spec-float-btn {
  height: 32px;
  padding: 0 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
}

.spec-float-btn--ghost {
  background: #fff;
  border: 1px solid #e5e7eb;
  color: #4b5563;
}

.spec-float-btn--ghost:hover {
  background: #f9fafb;
}

.spec-float-btn--primary {
  background: #1a6aff;
  border: 1px solid #1a6aff;
  color: #fff;
}

.spec-float-btn--primary:hover {
  background: #1557e6;
  border-color: #1557e6;
}
</style>
