<template>
  <div>
    <!-- 宝石银行 -->
    <div class="pixel-card rounded-xl p-4 mb-4">
      <div class="flex justify-between items-center mb-3">
        <h2 class="font-bold text-amber-900 text-lg flex items-center gap-2">
          <span class="text-2xl">🏦</span> 宝石银行
        </h2>
      </div>
      <div class="grid grid-cols-2 gap-3 mb-3">
        <div class="bg-teal-50 rounded-lg p-3 text-center">
          <div class="flex items-center justify-center gap-1 text-xl font-bold text-teal-600">
            <PixelIcon type="gem" :size="18" />{{ bank?.wallet_balance ?? 0 }}
          </div>
          <div class="text-[10px] text-amber-700 mt-1">钱包宝石</div>
        </div>
        <div class="bg-blue-50 rounded-lg p-3 text-center">
          <div class="flex items-center justify-center gap-1 text-xl font-bold text-blue-600">
            <PixelIcon type="gem" :size="18" />{{ bank?.bank_balance ?? 0 }}
          </div>
          <div class="text-[10px] text-amber-700 mt-1">银行存币</div>
        </div>
      </div>
      <!-- 利息直观展示：存钱会变多 -->
      <div v-if="bank && bank.bank_balance > 0" class="bg-gradient-to-r from-amber-50 to-yellow-50 rounded-lg p-3 mb-3 border-2 border-dashed border-amber-300">
        <div class="flex items-center gap-1 text-sm font-bold text-amber-700 mb-1">
          <span class="text-xl">📈</span> 存钱会变多哦！
        </div>
        <div class="flex flex-wrap gap-2 text-xs">
          <span class="bg-amber-100 text-amber-800 px-2 py-1 rounded-md font-bold">利率 {{ bank.interest_rate }}% / 周</span>
          <span class="bg-green-100 text-green-700 px-2 py-1 rounded-md font-bold">今天可增 {{ bank.today_interest }} 颗</span>
          <span class="bg-blue-100 text-blue-700 px-2 py-1 rounded-md font-bold">预计明日 {{ bank.expected_tomorrow }} 颗</span>
        </div>
      </div>
      <div class="flex gap-2 items-center">
        <input
          v-model="bankAmount"
          type="number"
          min="1"
          class="flex-1 p-2 rounded-lg border-2 border-amber-300 bg-white text-amber-900 text-sm outline-none focus:border-teal-400"
          placeholder="数量"
        />
        <button
          @click="doDeposit"
          :disabled="bankLoading || !bankAmount || bankAmount <= 0"
          class="pixel-btn btn-grass px-3 py-2 rounded-lg text-xs disabled:opacity-50"
        >存入</button>
        <button
          @click="doWithdraw"
          :disabled="bankLoading || !bankAmount || bankAmount <= 0"
          class="pixel-btn px-3 py-2 rounded-lg text-xs disabled:opacity-50"
          style="background: #3b82f6; color: white; border-color: #1e40af; box-shadow: 0 4px 0 #1e40af;"
        >取出</button>
      </div>
      <div v-if="bank?.records?.length" class="mt-3 space-y-1">
        <div class="text-[10px] text-amber-600 font-bold">最近记录</div>
        <div v-for="r in bank.records.slice(0, 3)" :key="r.id" class="text-[10px] flex justify-between">
          <span :class="r.action === 'deposit' ? 'text-blue-600' : 'text-teal-600'">
            {{ r.action === 'deposit' ? '存入' : '取出' }} {{ r.amount }}
          </span>
          <span class="text-amber-400">{{ r.created_at }}</span>
        </div>
      </div>
    </div>

    <!-- 惊喜奖励券 -->
    <div class="pixel-card rounded-xl p-4 mb-4">
      <div class="flex justify-between items-center mb-3">
        <h2 class="font-bold text-amber-900 text-lg flex items-center gap-2">
          <span class="text-2xl">🎫</span> 惊喜奖励券
        </h2>
      </div>
      <!-- 待使用的券 -->
      <div v-if="purchasedTickets.length" class="mb-3">
        <div class="text-[10px] text-purple-600 font-bold mb-1">我的奖励券（待使用）</div>
        <div
          v-for="t in purchasedTickets"
          :key="t.id"
          class="ticket-card rounded-lg p-3 mb-2 flex items-center justify-between"
        >
          <div>
            <div class="font-bold text-sm text-purple-800">🎁 {{ t.name }}</div>
            <div class="text-[10px] text-amber-600">{{ t.description || '神秘奖励' }}</div>
          </div>
          <button
            @click="useTicket(t)"
            class="pixel-btn btn-grass px-3 py-1.5 rounded-lg text-xs"
          >使用</button>
        </div>
      </div>
      <!-- 可购买的券 -->
      <div v-if="availableTickets.length">
        <div class="text-[10px] text-amber-600 font-bold mb-1">可购买的券</div>
        <div class="grid grid-cols-2 gap-2">
          <div
            v-for="t in availableTickets"
            :key="t.id"
            class="ticket-card rounded-lg p-3 text-center"
          >
            <div class="text-2xl mb-1">🎁</div>
            <div class="text-sm font-bold text-purple-800">{{ t.name }}</div>
            <div class="text-[10px] text-amber-600 mb-2">{{ t.description }}</div>
            <button
              @click="purchaseTicket(t)"
              :disabled="ticketLoading"
              class="pixel-btn btn-grass px-2 py-1 rounded-lg text-xs w-full"
            >
              <PixelIcon type="gem" :size="12" class="inline mr-1" />{{ t.cost }}
            </button>
          </div>
        </div>
      </div>
      <EmptyState
        v-if="!availableTickets.length && !purchasedTickets.length"
        icon="🎟️" text="暂无惊喜奖励券"
      />
    </div>

    <!-- 奖励商城 -->
    <div class="pixel-card rounded-xl p-4 mb-4">
      <div class="flex justify-between items-center mb-3">
        <h2 class="font-bold text-amber-900 text-lg">可兑换奖励</h2>
        <router-link to="/login" class="text-teal-600 text-sm font-bold">家长管理 →</router-link>
      </div>
      <div v-if="rewards.length" class="grid grid-cols-2 gap-3">
        <div
          v-for="r in rewards"
          :key="r.id"
          class="reward-card pixel-btn flex flex-col items-center p-3"
        >
          <PixelIcon type="reward" :reward-key="rewardKey(r.name)" :size="36" class="mb-1" />
          <div class="text-sm font-bold text-amber-900">{{ r.name }}</div>
          <div class="flex items-center gap-1 mt-1">
            <PixelIcon type="gem" :size="16" />
            <span class="text-teal-700 font-bold text-sm">{{ r.cost }}</span>
          </div>
        </div>
      </div>
      <EmptyState v-else icon="🎁" text="暂无可兑换奖励" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import PixelIcon from '@/components/game/PixelIcon.vue'
import EmptyState from '@/components/game/EmptyState.vue'
import { api } from '@/api'
import { useAppStore } from '@/stores/app'
import { useEffectStore } from '@/stores/effect'
import { useToastStore } from '@/stores/toast'
import { playSound } from '@/utils/sound'

const store = useAppStore()
const effectStore = useEffectStore()
const toast = useToastStore()

const rewards = ref<any[]>([])
const bank = ref<any>(null)
const bankAmount = ref<number | null>(null)
const bankLoading = ref(false)
const tickets = ref<any[]>([])
const ticketLoading = ref(false)

const purchasedTickets = computed(() => tickets.value.filter((t) => t.status === 'purchased'))
const availableTickets = computed(() => tickets.value.filter((t) => t.status === 'available' && t.enabled))

function rewardKey(name: string): string {
  if (name.includes('电视')) return 'tv'
  if (name.includes('平板')) return 'tablet'
  if (name.includes('零食')) return 'snack'
  return 'gift'
}

async function doDeposit() {
  const amt = bankAmount.value
  if (!amt || amt <= 0) return
  bankLoading.value = true
  try {
    await api.deposit(amt)
    playSound('gem')
    await store.refreshBalance()
    await loadBank()
    bankAmount.value = null
    toast.success('存入成功！')
  } catch (e: any) {
    toast.error(e.message || '存入失败')
  } finally {
    bankLoading.value = false
  }
}

async function doWithdraw() {
  const amt = bankAmount.value
  if (!amt || amt <= 0) return
  bankLoading.value = true
  try {
    await api.withdraw(amt)
    playSound('click')
    await store.refreshBalance()
    await loadBank()
    bankAmount.value = null
    toast.success('取出成功！')
  } catch (e: any) {
    toast.error(e.message || '取出失败')
  } finally {
    bankLoading.value = false
  }
}

async function purchaseTicket(t: any) {
  ticketLoading.value = true
  try {
    const res = await api.purchaseTicket(t.id)
    playSound('gem')
    await store.refreshBalance()
    effectStore.handleApiResponse(res)
    await loadTickets()
  } catch (e: any) {
    toast.error(e.message || '购买失败')
  } finally {
    ticketLoading.value = false
  }
}

async function useTicket(t: any) {
  if (!confirm(`使用奖励券「${t.name}」？`)) return
  try {
    await api.useTicket(t.id)
    playSound('click')
    toast.success('奖励券已使用！')
    await loadTickets()
  } catch (e: any) {
    toast.error(e.message || '使用失败')
  }
}

async function loadBank() {
  bank.value = await api.getBank()
}
async function loadTickets() {
  tickets.value = await api.getTickets()
}

async function load() {
  try {
    await store.loadCore()
    const [rew, bnk, tkts] = await Promise.all([
      api.getRewards(),
      api.getBank(),
      api.getTickets(),
    ])
    rewards.value = rew.filter((r: any) => r.enabled)
    bank.value = bnk
    tickets.value = tkts
  } catch (e: any) {
    console.error(e)
  }
}

onMounted(load)
</script>

<style scoped>
.ticket-card {
  background: linear-gradient(135deg, #f3e5f5, #e1bee7);
  border: 2px solid #ce93d8;
}
.reward-card {
  background: linear-gradient(180deg, #fffde7 0%, #fff8e1 100%);
  border-color: #ffb300;
  box-shadow: 0 3px 0 #e65100;
}
</style>
