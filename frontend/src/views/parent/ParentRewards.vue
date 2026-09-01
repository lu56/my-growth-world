<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-xl font-bold pixel-font text-amber-900">奖励商城</h1>
      <div class="flex items-center gap-1 bg-amber-100 px-3 py-1 rounded-full">
        <PixelIcon type="gem" :size="18" />
        <span class="font-bold text-teal-700">{{ balance }}</span>
      </div>
    </div>
    <button @click="openCreate" class="pixel-btn btn-grass px-3 py-2 rounded-lg text-sm mb-3">
      + 新增奖励
    </button>

    <div class="grid grid-cols-2 gap-3">
      <div
        v-for="r in rewards"
        :key="r.id"
        class="pixel-card rounded-xl p-3 text-center relative"
        :class="r.enabled ? '' : 'opacity-50'"
      >
        <div class="mb-1 flex justify-center">
          <PixelIcon type="reward" :reward-key="rewardKey(r.name)" :size="36" />
        </div>
        <div class="font-bold text-sm text-amber-900">{{ r.name }}</div>
        <div class="text-xs text-amber-600 mt-1">{{ r.description }}</div>
        <div class="flex items-center justify-center gap-1 mt-1">
          <PixelIcon type="gem" :size="16" />
          <span class="text-teal-700 font-bold">{{ r.cost }}</span>
        </div>
        <!-- 兑换按钮 -->
        <button
          v-if="r.enabled"
          @click="confirmExchange(r)"
          class="pixel-btn w-full mt-2 py-1 rounded-lg text-sm"
          :class="balance >= r.cost ? 'btn-gem' : 'btn-wood'"
          :disabled="balance < r.cost || exchanging"
        >
          {{ balance >= r.cost ? '兑换' : '宝石不足' }}
        </button>
        <div class="flex gap-2 mt-2 justify-center">
          <button @click="toggle(r)" class="pixel-btn text-xs px-2 py-1 rounded btn-wood">
            {{ r.enabled ? '停用' : '启用' }}
          </button>
          <button @click="remove(r)" class="pixel-btn text-xs px-2 py-1 rounded btn-red">删除</button>
        </div>
      </div>
    </div>

    <!-- 兑换确认弹窗 -->
    <div v-if="exchangeTarget" class="fixed inset-0 flex items-center justify-center p-4 z-30" @click.self="exchangeTarget = null">
      <div class="overlay-bg"></div>
      <div class="pixel-card rounded-xl p-5 text-center relative max-w-sm w-full" @click.stop>
        <div class="flex justify-center mb-3">
          <PixelIcon type="reward" :reward-key="rewardKey(exchangeTarget.name)" :size="48" />
        </div>
        <h2 class="font-bold text-lg text-amber-900 mb-2">确认兑换</h2>
        <div class="text-amber-700 text-sm mb-1">{{ exchangeTarget.name }}</div>
        <div class="flex items-center justify-center gap-1 mb-4">
          <PixelIcon type="gem" :size="20" />
          <span class="text-teal-700 font-bold text-lg">{{ exchangeTarget.cost }}</span>
        </div>
        <div class="text-xs text-amber-600 mb-4">
          兑换后余额：{{ balance - exchangeTarget.cost }} 宝石
        </div>
        <div v-if="exchanging" class="py-4">
          <div class="flex justify-center mb-2"><PixelIcon type="gem" :size="40" class="anim-spin" /></div>
          <div class="text-sm text-amber-600">兑换中...</div>
        </div>
        <div v-else class="flex gap-3">
          <button @click="exchangeTarget = null" class="flex-1 pixel-btn py-2 rounded-lg btn-wood">取消</button>
          <button @click="doExchange" class="flex-1 pixel-btn py-2 rounded-lg btn-gem">确认兑换</button>
        </div>
      </div>
    </div>

    <!-- 新增弹窗 -->
    <div v-if="showForm" class="fixed inset-0 flex items-center justify-center p-4 z-20" @click.self="showForm = false">
      <div class="overlay-bg"></div>
      <div class="pixel-card rounded-xl p-5 relative max-w-sm w-full" @click.stop>
        <h2 class="font-bold mb-4 text-amber-900">新增奖励</h2>
        <label class="block text-sm mb-1 text-amber-800">名称</label>
        <input v-model="form.name" class="w-full p-2 mb-3 rounded-lg border-2 border-amber-300 bg-white text-amber-900 outline-none focus:border-teal-400" />
        <label class="block text-sm mb-1 text-amber-800">所需宝石</label>
        <input v-model.number="form.cost" type="number" class="w-full p-2 mb-3 rounded-lg border-2 border-amber-300 bg-white text-amber-900 outline-none focus:border-teal-400" />
        <label class="block text-sm mb-1 text-amber-800">说明</label>
        <input v-model="form.description" class="w-full p-2 mb-4 rounded-lg border-2 border-amber-300 bg-white text-amber-900 outline-none focus:border-teal-400" />
        <div class="flex gap-3">
          <button @click="showForm = false" class="flex-1 pixel-btn py-2 rounded-lg btn-wood">取消</button>
          <button @click="save" class="flex-1 pixel-btn py-2 rounded-lg btn-grass">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, computed } from 'vue'
import { api } from '@/api'
import { useAppStore } from '@/stores/app'
import { useEffectStore } from '@/stores/effect'
import { useToastStore } from '@/stores/toast'
import { playSound } from '@/utils/sound'
import PixelIcon from '@/components/game/PixelIcon.vue'

const store = useAppStore()
const effectStore = useEffectStore()
const toast = useToastStore()
const rewards = ref<any[]>([])
const showForm = ref(false)
const exchangeTarget = ref<any>(null)
const exchanging = ref(false)
const form = reactive({ name: '', cost: 30, description: '' })

const balance = computed(() => store.balance)

function rewardKey(name: string): string {
  if (name.includes('电视')) return 'tv'
  if (name.includes('平板')) return 'tablet'
  if (name.includes('零食')) return 'snack'
  return 'gift'
}

async function load() {
  rewards.value = await api.getRewards()
}

function openCreate() {
  Object.assign(form, { name: '', cost: 30, description: '' })
  showForm.value = true
}

async function save() {
  if (!form.name) return
  await api.createReward({ ...form })
  showForm.value = false
  await load()
}

async function toggle(r: any) {
  await api.updateReward(r.id, { enabled: !r.enabled })
  await load()
}

async function remove(r: any) {
  if (confirm(`删除奖励「${r.name}」？`)) {
    await api.deleteReward(r.id)
    await load()
  }
}

function confirmExchange(r: any) {
  if (balance.value < r.cost) return
  playSound('click')
  exchangeTarget.value = r
}

async function doExchange() {
  if (!exchangeTarget.value) return
  exchanging.value = true
  try {
    const res = await api.exchange({ reward_id: exchangeTarget.value.id })
    await store.refreshBalance()
    playSound('exchange')
    exchangeTarget.value = null
    effectStore.handleApiResponse(res)
    await load()
  } catch (e: any) {
    toast.error(e.message || '兑换失败')
  } finally {
    exchanging.value = false
  }
}

onMounted(async () => {
  await load()
  await store.refreshBalance()
})
</script>

<style scoped>
.overlay-bg {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
}

.anim-spin {
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
