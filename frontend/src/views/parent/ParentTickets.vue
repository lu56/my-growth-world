<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-xl font-bold pixel-font text-amber-900">惊喜奖励券</h1>
      <button @click="openForm" class="pixel-btn btn-grass px-3 py-2 rounded-lg text-sm">
        + 新建券
      </button>
    </div>

    <!-- 统计 -->
    <div class="grid grid-cols-3 gap-2 mb-4">
      <div class="pixel-card rounded-xl p-2 text-center">
        <div class="text-lg font-bold text-teal-600">{{ availableCount }}</div>
        <div class="text-[10px] text-amber-700">可购买</div>
      </div>
      <div class="pixel-card rounded-xl p-2 text-center">
        <div class="text-lg font-bold text-purple-600">{{ purchasedCount }}</div>
        <div class="text-[10px] text-amber-700">待使用</div>
      </div>
      <div class="pixel-card rounded-xl p-2 text-center">
        <div class="text-lg font-bold text-green-600">{{ usedCount }}</div>
        <div class="text-[10px] text-amber-700">已使用</div>
      </div>
    </div>

    <!-- 奖励券列表 -->
    <div class="pixel-card rounded-xl p-4">
      <div v-if="tickets.length" class="space-y-3">
        <div
          v-for="t in tickets"
          :key="t.id"
          class="rounded-lg p-3 border-2"
          :class="ticketCardClass(t)"
        >
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <div class="font-bold text-sm text-amber-900 flex items-center gap-1">
                🎫 {{ t.name }}
              </div>
              <p v-if="t.description" class="text-xs text-amber-600 mt-1">{{ t.description }}</p>
              <div class="flex items-center gap-2 mt-1">
                <span class="flex items-center gap-1 text-xs text-teal-700 font-bold">
                  <PixelIcon type="gem" :size="12" /> {{ t.cost }}
                </span>
                <span class="text-[10px] px-2 py-0.5 rounded-full font-bold" :class="ticketStatusClass(t)">
                  {{ ticketStatusLabel(t) }}
                </span>
                <span v-if="!t.enabled" class="text-[10px] text-red-500">已停用</span>
              </div>
              <div v-if="t.purchased_at" class="text-[10px] text-amber-400 mt-1">购买：{{ t.purchased_at }}</div>
              <div v-if="t.used_at" class="text-[10px] text-amber-400">使用：{{ t.used_at }}</div>
            </div>
            <button
              v-if="t.status === 'available'"
              @click="removeTicket(t)"
              class="pixel-btn text-xs px-2 py-1 rounded btn-red"
            >删除</button>
          </div>
        </div>
      </div>
      <div v-else class="text-center text-amber-500 text-sm py-6">
        暂无奖励券，点击右上角新建
      </div>
    </div>

    <!-- 新建弹窗 -->
    <div v-if="showForm" class="fixed inset-0 flex items-center justify-center p-4 z-20" @click.self="showForm = false">
      <div class="overlay-bg"></div>
      <div class="pixel-card rounded-xl p-5 relative max-w-sm w-full" @click.stop>
        <h2 class="font-bold mb-4 text-amber-900">新建奖励券</h2>
        <label class="block text-sm mb-1 text-amber-800">奖励名称</label>
        <input v-model="form.name" placeholder="如：免做家务一次" class="w-full p-2 mb-3 rounded-lg border-2 border-amber-300 bg-white text-amber-900 outline-none focus:border-teal-400" />
        <label class="block text-sm mb-1 text-amber-800">说明（可选）</label>
        <input v-model="form.description" placeholder="奖励内容描述" class="w-full p-2 mb-3 rounded-lg border-2 border-amber-300 bg-white text-amber-900 outline-none focus:border-teal-400" />
        <label class="block text-sm mb-1 text-amber-800">购买所需宝石</label>
        <input v-model.number="form.cost" type="number" min="1" class="w-full p-2 mb-4 rounded-lg border-2 border-amber-300 bg-white text-amber-900 outline-none focus:border-teal-400" />
        <div class="flex gap-3">
          <button @click="showForm = false" class="flex-1 pixel-btn py-2 rounded-lg btn-wood">取消</button>
          <button @click="save" :disabled="!form.name" class="flex-1 pixel-btn py-2 rounded-lg btn-grass disabled:opacity-50">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, computed } from 'vue'
import { api } from '@/api'
import { playSound } from '@/utils/sound'
import PixelIcon from '@/components/game/PixelIcon.vue'

const tickets = ref<any[]>([])
const showForm = ref(false)
const form = reactive({ name: '', description: '', cost: 10 })

const availableCount = computed(() => tickets.value.filter((t) => t.status === 'available' && t.enabled).length)
const purchasedCount = computed(() => tickets.value.filter((t) => t.status === 'purchased').length)
const usedCount = computed(() => tickets.value.filter((t) => t.status === 'used').length)

function ticketCardClass(t: any): string {
  if (t.status === 'used') return 'border-green-300 bg-green-50'
  if (t.status === 'purchased') return 'border-purple-400 bg-purple-50'
  if (!t.enabled) return 'border-red-300 bg-red-50'
  return 'border-amber-300 bg-amber-50'
}

function ticketStatusClass(t: any): string {
  const map: Record<string, string> = {
    available: 'bg-teal-200 text-teal-700',
    purchased: 'bg-purple-200 text-purple-700',
    used: 'bg-green-200 text-green-700',
  }
  return map[t.status] || ''
}

function ticketStatusLabel(t: any): string {
  const map: Record<string, string> = {
    available: '可购买',
    purchased: '待使用',
    used: '已使用',
  }
  return map[t.status] || t.status
}

async function load() {
  tickets.value = await api.getTickets()
}

function openForm() {
  playSound('click')
  Object.assign(form, { name: '', description: '', cost: 10 })
  showForm.value = true
}

async function save() {
  if (!form.name) return
  await api.createTicket({ name: form.name, description: form.description, cost: form.cost })
  showForm.value = false
  playSound('click')
  await load()
}

async function removeTicket(t: any) {
  if (confirm(`删除奖励券「${t.name}」？`)) {
    await api.deleteTicket(t.id)
    await load()
  }
}

onMounted(load)
</script>

<style scoped>
.overlay-bg {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
}
</style>
