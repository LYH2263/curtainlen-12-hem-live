<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, patchJSON } from '../api'
const items = ref([])
const error = ref('')
onMounted(load)
async function load(){
  items.value = (await getJSON('/api/fabrics')).items
  items.value.forEach(f => { f._top = f.hem_top; f._bottom = f.hem_bottom })
}
function asNum(v){ const n = parseFloat(v); return Number.isFinite(n) ? n : NaN }
async function save(f){
  error.value = ''
  const top = asNum(f.hem_top); const bottom = asNum(f.hem_bottom)
  if (!Number.isFinite(top) || !Number.isFinite(bottom) || top < 0 || bottom < 0) {
    error.value = '折边不能为负'
    f.hem_top = f._top; f.hem_bottom = f._bottom
    return
  }
  try {
    const r = await patchJSON(`/api/fabrics/${f.id}/hems`, { hem_top: top, hem_bottom: bottom })
    f.hem_top = r.hem_top; f.hem_bottom = r.hem_bottom
    f._top = r.hem_top; f._bottom = r.hem_bottom
  } catch (e) {
    error.value = '保存失败，已保留原折边'
    f.hem_top = f._top; f.hem_bottom = f._bottom
  }
}
</script>
<template><div class="page"><h1>面料</h1>
<p v-if="error" class="bad">{{ error }}</p>
<div v-for="f in items" :key="f.id" class="fab">
  {{ f.name }} 门幅{{ f.fabric_width }}m
  <label>上折边<input type="number" step="0.01" min="0" v-model.number="f.hem_top"></label>
  <label>下折边<input type="number" step="0.01" min="0" v-model.number="f.hem_bottom"></label>
  <button @click="save(f)">保存</button>
</div></div></template>
