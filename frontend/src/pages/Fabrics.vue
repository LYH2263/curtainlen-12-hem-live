<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const items = ref([])
const msg = ref({})
onMounted(async () => { items.value = (await getJSON('/api/fabrics')).items })
async function save(f) {
  msg.value = { ...msg.value, [f.id]: '' }
  try {
    const u = await putJSON(`/api/fabrics/${f.id}/hems`, { hem_top: Number(f.hem_top), hem_bottom: Number(f.hem_bottom) })
    f.hem_top = u.hem_top
    f.hem_bottom = u.hem_bottom
    msg.value = { ...msg.value, [f.id]: '已保存' }
  } catch (e) {
    // 接口拒绝（如负数）时回退为库中原值，保证展示与仓储一致
    const fresh = await getJSON(`/api/fabrics/${f.id}`)
    f.hem_top = fresh.hem_top
    f.hem_bottom = fresh.hem_bottom
    msg.value = { ...msg.value, [f.id]: '保存失败：折边须为非负数值' }
  }
}
</script>
<template>
  <div class="page"><h1>面料</h1>
    <div v-for="f in items" :key="f.id" class="fab">
      <strong>{{ f.name }}</strong> 门幅{{ f.fabric_width }}m
      上折边 <input v-model.number="f.hem_top" type="number" step="0.01" min="0" style="width:5rem"> m
      下折边 <input v-model.number="f.hem_bottom" type="number" step="0.01" min="0" style="width:5rem"> m
      <button @click="save(f)">保存</button>
      <span :class="{ bad: msg[f.id] && msg[f.id] !== '已保存' }">{{ msg[f.id] }}</span>
    </div>
  </div>
</template>
