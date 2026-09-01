<template>
  <div>
    <h1 class="text-xl font-bold mb-4 pixel-font text-amber-900">家长设置</h1>

    <!-- 孩子信息 -->
    <div class="pixel-card rounded-xl p-4 mb-4">
      <h2 class="font-bold mb-3 text-amber-900">孩子信息</h2>
      <label class="block text-sm mb-1 text-amber-800">孩子名称</label>
      <div class="flex gap-2">
        <input v-model="childName" class="flex-1 p-2 rounded-lg border-2 border-amber-300 bg-white text-amber-900 outline-none focus:border-teal-400" />
        <button @click="saveChild" class="pixel-btn btn-grass px-4 rounded-lg">保存</button>
      </div>
    </div>

    <!-- 修改家长口令 -->
    <div class="pixel-card rounded-xl p-4 mb-4">
      <h2 class="font-bold mb-3 text-amber-900">修改家长口令</h2>
      <label class="block text-sm mb-1 text-amber-800">新口令</label>
      <input v-model="newPassword" type="password" class="w-full p-2 mb-3 rounded-lg border-2 border-amber-300 bg-white text-amber-900 outline-none focus:border-teal-400" />
      <button @click="savePassword" class="pixel-btn btn-gem px-4 py-2 rounded-lg font-bold">
        更新口令
      </button>
      <p v-if="msg" class="text-green-600 text-sm mt-2 bg-green-50 px-3 py-1 rounded-lg">{{ msg }}</p>
    </div>

    <!-- 修改孩子口令 -->
    <div class="pixel-card rounded-xl p-4 mb-4">
      <h2 class="font-bold mb-3 text-amber-900">修改孩子口令</h2>
      <label class="block text-sm mb-1 text-amber-800">新口令</label>
      <input v-model="newChildPassword" type="password" class="w-full p-2 mb-3 rounded-lg border-2 border-amber-300 bg-white text-amber-900 outline-none focus:border-teal-400" />
      <button @click="saveChildPassword" class="pixel-btn btn-gem px-4 py-2 rounded-lg font-bold">
        更新孩子口令
      </button>
      <p v-if="msg" class="text-green-600 text-sm mt-2 bg-green-50 px-3 py-1 rounded-lg">{{ msg }}</p>
    </div>

    <!-- 银行利率 -->
    <div class="pixel-card rounded-xl p-4 mb-4">
      <h2 class="font-bold mb-3 text-amber-900">银行利率（%/周）</h2>
      <label class="block text-xs mb-1 text-amber-800">存进银行每周增值的百分比（0=不计息）</label>
      <input v-model.number="interestRate" type="number" min="0" step="0.1" class="w-full p-2 rounded-lg border-2 border-amber-300 bg-white text-amber-900 outline-none focus:border-teal-400" />
      <button @click="saveInterestRate" class="pixel-btn btn-grass mt-3 px-4 py-2 rounded-lg">保存</button>
      <p v-if="msg" class="text-green-600 text-sm mt-2 bg-green-50 px-3 py-1 rounded-lg">{{ msg }}</p>
    </div>

    <!-- 积分上限 -->
    <div class="pixel-card rounded-xl p-4">
      <h2 class="font-bold mb-3 text-amber-900">积分上限（0=不限）</h2>
      <div class="flex gap-3">
        <div class="flex-1">
          <label class="block text-xs mb-1 text-amber-800">单日上限</label>
          <input v-model.number="dailyLimit" type="number" class="w-full p-2 rounded-lg border-2 border-amber-300 bg-white text-amber-900 outline-none focus:border-teal-400" />
        </div>
        <div class="flex-1">
          <label class="block text-xs mb-1 text-amber-800">单周上限</label>
          <input v-model.number="weeklyLimit" type="number" class="w-full p-2 rounded-lg border-2 border-amber-300 bg-white text-amber-900 outline-none focus:border-teal-400" />
        </div>
      </div>
      <button @click="saveLimits" class="pixel-btn btn-grass mt-3 px-4 py-2 rounded-lg">保存</button>
      <p v-if="msg" class="text-green-600 text-sm mt-2 bg-green-50 px-3 py-1 rounded-lg">{{ msg }}</p>
    </div>

    <!-- 数据管理 -->
    <div class="pixel-card rounded-xl p-4 mt-4">
      <h2 class="font-bold mb-1 text-amber-900">数据管理</h2>
      <p class="text-xs text-amber-700 mb-3">备份或迁移家庭数据。导出为 JSON 文件，导入会覆盖现有数据，清理会清空全部记录。</p>
      <div class="flex flex-wrap gap-2">
        <button @click="exportData" class="pixel-btn btn-grass px-4 py-2 rounded-lg">导出数据</button>
        <label class="pixel-btn btn-gem px-4 py-2 rounded-lg cursor-pointer text-center">
          导入数据
          <input type="file" accept=".json,application/json" class="hidden" @change="onImportFile" />
        </label>
        <button @click="clearData" class="pixel-btn px-4 py-2 rounded-lg" style="background:#dc2626;color:#fff">一键清理</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '@/api'
import { useAppStore } from '@/stores/app'
import { useToastStore } from '@/stores/toast'

const store = useAppStore()
const toast = useToastStore()
const childName = ref('')
const newPassword = ref('')
const newChildPassword = ref('')
const dailyLimit = ref(0)
const weeklyLimit = ref(0)
const interestRate = ref(2)
const msg = ref('')

onMounted(async () => {
  try {
    const child = await api.getChild()
    childName.value = child.name
    const cfg = await api.getParentConfig()
    dailyLimit.value = cfg.daily_score_limit
    weeklyLimit.value = cfg.weekly_score_limit
    interestRate.value = cfg.bank_interest_rate ?? 2
  } catch (e) {
    console.error(e)
  }
})

async function saveChild() {
  const res = await fetch(`/api/child`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('gw_token')}` },
    body: JSON.stringify({ name: childName.value }),
  })
  if (res.ok) {
    await store.loadCore()
    msg.value = '孩子信息已保存'
    setTimeout(() => { msg.value = '' }, 3000)
  }
}

async function savePassword() {
  if (!newPassword.value) return
  await api.updateParentConfig({ new_password: newPassword.value })
  newPassword.value = ''
  msg.value = '家长口令已更新'
  setTimeout(() => { msg.value = '' }, 3000)
}

async function saveChildPassword() {
  if (!newChildPassword.value) return
  await api.updateParentConfig({ new_child_password: newChildPassword.value })
  newChildPassword.value = ''
  msg.value = '孩子口令已更新'
  setTimeout(() => { msg.value = '' }, 3000)
}

async function saveInterestRate() {
  await api.updateParentConfig({ bank_interest_rate: interestRate.value })
  msg.value = '银行利率已保存'
  setTimeout(() => { msg.value = '' }, 3000)
}

async function saveLimits() {
  await api.updateParentConfig({
    daily_score_limit: dailyLimit.value,
    weekly_score_limit: weeklyLimit.value,
  })
  msg.value = '上限已保存'
  setTimeout(() => { msg.value = '' }, 3000)
}

// 导出数据：下载 JSON 文件
async function exportData() {
  try {
    const data = await api.exportData()
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const date = new Date()
    const d = `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, '0')}${String(date.getDate()).padStart(2, '0')}`
    a.download = `growth-world-backup-${d}.json`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('数据已导出')
  } catch (e: any) {
    toast.error(e.message || '导出失败')
  }
}

// 导入数据：读取选择的 JSON 文件
async function onImportFile(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  const text = await file.text()
  let data: any
  try {
    data = JSON.parse(text)
  } catch {
    toast.error('文件不是有效的 JSON')
    return
  }
  if (!data || typeof data !== 'object') {
    toast.error('导入文件格式不正确')
    return
  }
  const ok = confirm('导入将覆盖当前全部业务数据，确定继续吗？')
  if (!ok) return
  try {
    await api.importData(data)
    toast.success('数据导入成功')
    await store.loadCore()
  } catch (e: any) {
    toast.error(e.message || '导入失败')
  }
}

// 一键清理：二次确认后清空业务数据并重置口令为 admin123
async function clearData() {
  const ok = confirm('一键清理将删除所有积分、打卡、银行等记录，并重置口令为 admin123，且不可恢复！确定继续吗？')
  if (!ok) return
  try {
    await api.clearData()
    toast.success('已清理并恢复默认设置')
    await store.loadCore()
  } catch (e: any) {
    toast.error(e.message || '清理失败')
  }
}
</script>
