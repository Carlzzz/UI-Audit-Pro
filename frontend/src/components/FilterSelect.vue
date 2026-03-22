<template>
  <div ref="rootRef" class="filter-select-root">
    <button
      type="button"
      class="filter-select-trigger"
      :class="{ 'is-open': open }"
      :aria-expanded="open"
      :aria-haspopup="true"
      @click="open = !open"
    >
      <span class="filter-select-label">{{ displayLabel }}</span>
    </button>
    <ul v-show="open" class="filter-select-menu" role="listbox" :aria-label="menuLabel">
      <li
        v-for="opt in options"
        :key="String(opt.value)"
        role="option"
        :aria-selected="modelValue === opt.value"
        class="filter-select-option"
        :class="{ 'is-selected': modelValue === opt.value }"
        @mousedown.prevent="pick(opt.value)"
      >
        {{ opt.label }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  modelValue: { type: [String, Number], required: true },
  options: {
    type: Array,
    required: true
  },
  /** 无障碍：列表用途说明 */
  menuLabel: { type: String, default: '选项' }
})

const emit = defineEmits(['update:modelValue'])

const open = ref(false)
const rootRef = ref(null)

const displayLabel = computed(() => {
  const hit = props.options.find((o) => o.value === props.modelValue)
  return hit?.label ?? ''
})

function pick(value) {
  emit('update:modelValue', value)
  open.value = false
}

function onDocPointerDown(e) {
  if (!open.value || !rootRef.value) return
  if (!rootRef.value.contains(e.target)) open.value = false
}

function onKeydown(e) {
  if (e.key === 'Escape') open.value = false
}

onMounted(() => {
  document.addEventListener('pointerdown', onDocPointerDown, true)
  document.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  document.removeEventListener('pointerdown', onDocPointerDown, true)
  document.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
.filter-select-root {
  position: relative;
  width: 100%;
  min-width: 0;
}

.filter-select-trigger {
  width: 100%;
  box-sizing: border-box;
  margin: 0;
  padding: 9px 36px 9px 12px;
  border: 1px solid #dbe0ea;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  font-weight: 400;
  background-color: #fff;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%236b7280' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 16px;
  color: #374151;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.filter-select-trigger:hover {
  border-color: #c5cce0;
}

.filter-select-trigger:focus {
  outline: none;
  border-color: #8aa7ff;
  box-shadow: 0 0 0 3px rgba(26, 106, 255, 0.12);
}

.filter-select-label {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.filter-select-menu {
  position: absolute;
  left: 0;
  right: 0;
  top: calc(100% + 4px);
  margin: 0;
  padding: 6px 0;
  list-style: none;
  background: #fff;
  border: 1px solid #dbe0ea;
  border-radius: 8px;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.12), 0 0 0 1px rgba(15, 23, 42, 0.04);
  z-index: 200;
  max-height: 280px;
  overflow-y: auto;
}

.filter-select-option {
  padding: 9px 12px;
  font-size: 14px;
  color: #374151;
  cursor: pointer;
  user-select: none;
}

.filter-select-option:hover,
.filter-select-option:focus {
  background: #f3f6ff;
  outline: none;
}

.filter-select-option.is-selected {
  background: #eef2ff;
  color: #1a6aff;
  font-weight: 600;
}
</style>
