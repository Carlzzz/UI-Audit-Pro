<template>
  <Teleport to="body">
    <div
      v-show="open"
      ref="panelRef"
      class="spec-float-panel"
      :style="panelStyle"
      role="dialog"
      aria-modal="true"
      @click.stop
    >
      <div class="spec-float-title">{{ title }}</div>

      <div v-if="mode === 'xy'" class="spec-float-field">
        <span class="spec-float-label">{{ fieldLabel }}</span>
        <div class="spec-float-inputs">
          <input v-model="wPart" type="text" class="spec-float-input" autocomplete="off" />
          <span class="spec-float-sep">×</span>
          <input v-model="hPart" type="text" class="spec-float-input" autocomplete="off" />
          <span class="spec-float-unit">px</span>
        </div>
      </div>

      <div v-else class="spec-float-field">
        <span class="spec-float-label">{{ fieldLabel }}</span>
        <div class="spec-float-inputs">
          <input v-model="vSingle" type="text" class="spec-float-input spec-float-input--grow" autocomplete="off" />
          <span v-if="mode === 'px'" class="spec-float-unit">px</span>
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
  title: { type: String, default: '' },
  fieldLabel: { type: String, default: '规范值' },
  defaultVal: { type: String, default: '' },
  /** px | xy | plain */
  mode: { type: String, default: 'plain' },
})

const emit = defineEmits(['update:open', 'confirm'])

const panelRef = ref(null)
const vSingle = ref('')
const wPart = ref('')
const hPart = ref('')

const panelStyle = computed(() => ({
  left: `${props.left}px`,
  top: `${props.top}px`,
}))

function initFromDefault() {
  const d = String(props.defaultVal ?? '').trim()
  if (props.mode === 'xy') {
    const stripped = d.replace(/px$/i, '')
    const parts = stripped.split('*')
    wPart.value = parts[0] ?? ''
    hPart.value = parts[1] ?? ''
  } else if (props.mode === 'px') {
    vSingle.value = d.replace(/px$/i, '')
  } else {
    vSingle.value = d
  }
}

function close() {
  emit('update:open', false)
}

function submit() {
  if (props.mode === 'xy') {
    const w = wPart.value.trim()
    const h = hPart.value.trim()
    if (!w || !h) return
    emit('confirm', `${w}*${h}px`)
  } else if (props.mode === 'px') {
    const v = vSingle.value.trim()
    if (!v) return
    emit('confirm', /px$/i.test(v) ? v : `${v}px`)
  } else {
    const v = vSingle.value.trim()
    if (!v) return
    emit('confirm', v)
  }
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
      initFromDefault()
      await nextTick()
      offDoc = (e) => {
        if (panelRef.value && !panelRef.value.contains(e.target)) close()
      }
      setTimeout(() => document.addEventListener('mousedown', offDoc), 0)
    }
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

.spec-float-input {
  height: 32px;
  padding: 0 10px;
  border: 1px solid #e2e4ec;
  border-radius: 8px;
  font-size: 14px;
  color: #1a1d2e;
  background: #fff;
  width: 88px;
  box-sizing: border-box;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.spec-float-input--grow {
  flex: 1;
  min-width: 120px;
  width: auto;
}

.spec-float-input:hover {
  border-color: #1a6aff;
}

.spec-float-input:focus {
  border-color: #1a6aff;
  box-shadow: 0 0 0 2px rgba(26, 106, 255, 0.15);
}

.spec-float-sep {
  color: #9ca3af;
  font-weight: 600;
}

.spec-float-unit {
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
  flex-shrink: 0;
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
