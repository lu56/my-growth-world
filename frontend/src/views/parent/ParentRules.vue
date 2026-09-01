<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-xl font-bold pixel-font text-amber-900">任务规则</h1>
      <button @click="openCreate" class="pixel-btn btn-grass px-3 py-2 rounded-lg text-sm">
        + 新建规则
      </button>
    </div>

    <div class="pixel-card rounded-xl p-4">
      <div class="divide-y divide-amber-200">
        <div v-for="t in tasks" :key="t.id" class="py-3 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <PixelIcon type="task" :task-type="t.task_type" :size="28" />
            <div>
              <div class="font-medium text-amber-900">{{ t.name }}</div>
              <div class="text-xs text-amber-600">
                {{ t.task_type }} · {{ t.enabled ? '启用' : '停用' }} · {{ t.is_checkin ? '可打卡' : '手动记' }}
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span
              class="font-bold px-2 py-1 rounded-lg text-sm"
              :class="t.score_value > 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
            >
              {{ t.score_value > 0 ? '+' : '' }}{{ t.score_value }}
            </span>
            <!-- 可打卡开关 -->
            <button
              @click="toggleCheckin(t)"
              class="px-2 py-1 rounded-lg text-[10px] font-bold transition-colors"
              :class="t.is_checkin ? 'bg-teal-200 text-teal-700' : 'bg-gray-200 text-gray-500'"
            >
              {{ t.is_checkin ? '打卡' : '手动' }}
            </button>
            <button
              @click="openEdit(t)"
              class="pixel-btn text-xs px-2 py-1 rounded btn-wood"
            >编辑</button>
            <button
              @click="remove(t)"
              class="pixel-btn text-xs px-2 py-1 rounded btn-red"
            >删除</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建/编辑弹窗 -->
    <div v-if="showForm" class="fixed inset-0 flex items-center justify-center p-4 z-20" @click.self="showForm = false">
      <div class="overlay-bg"></div>
      <div class="pixel-card rounded-xl p-5 relative max-w-sm w-full" @click.stop>
        <h2 class="font-bold mb-4 text-amber-900">{{ form.id ? '编辑规则' : '新建规则' }}</h2>
        <label class="block text-sm mb-1 text-amber-800">名称</label>
        <input v-model="form.name" class="w-full p-2 mb-3 rounded-lg border-2 border-amber-300 bg-white text-amber-900 outline-none focus:border-teal-400" />
        <label class="block text-sm mb-1 text-amber-800">类型</label>
        <select v-model="form.task_type" class="w-full p-2 mb-3 rounded-lg border-2 border-amber-300 bg-white text-amber-900">
          <option v-for="ty in types" :key="ty" :value="ty">{{ ty }}</option>
        </select>
        <label class="block text-sm mb-1 text-amber-800">分值（正数奖励 / 负数惩罚）</label>
        <input v-model.number="form.score_value" type="number" class="w-full p-2 mb-3 rounded-lg border-2 border-amber-300 bg-white text-amber-900 outline-none focus:border-teal-400" />
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
import { onMounted, reactive, ref } from 'vue'
import { api } from '@/api'
import { useToastStore } from '@/stores/toast'
import { playSound } from '@/utils/sound'
import PixelIcon from '@/components/game/PixelIcon.vue'

const toast = useToastStore()

const tasks = ref<any[]>([])
const showForm = ref(false)
const types = ['学习', '家务', '习惯', '品德', '临时']
const form = reactive<any>({ id: null, name: '', task_type: '学习', score_value: 5, description: '', is_checkin: false })

async function load() {
  tasks.value = await api.getTasks()
}

function openCreate() {
  playSound('click')
  Object.assign(form, { id: null, name: '', task_type: '学习', score_value: 5, description: '', is_checkin: false })
  showForm.value = true
}

function openEdit(t: any) {
  playSound('click')
  Object.assign(form, {
    id: t.id,
    name: t.name,
    task_type: t.task_type,
    score_value: t.score_value,
    description: t.description || '',
    is_checkin: !!t.is_checkin,
  })
  showForm.value = true
}

async function save() {
  if (!form.name) return
  if (form.id) {
    await api.updateTask(form.id, { name: form.name, task_type: form.task_type, score_value: form.score_value, description: form.description, is_checkin: form.is_checkin })
  } else {
    await api.createTask({ name: form.name, task_type: form.task_type, score_value: form.score_value, description: form.description, is_checkin: form.is_checkin })
  }
  showForm.value = false
  await load()
}

async function toggleCheckin(t: any) {
  try {
    await api.updateTask(t.id, { is_checkin: !t.is_checkin })
    t.is_checkin = !t.is_checkin
    playSound('click')
  } catch (e: any) {
    toast.error(e.message || '操作失败')
  }
}

async function remove(t: any) {
  if (confirm(`删除规则「${t.name}」？`)) {
    await api.deleteTask(t.id)
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
