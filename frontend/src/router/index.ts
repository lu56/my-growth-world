import { createRouter, createWebHistory } from 'vue-router'
import { getToken, getRole } from '@/api'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/home',
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/Login.vue'),
      meta: { title: '登录' },
    },
    {
      path: '/',
      component: () => import('@/views/child/ChildLayout.vue'),
      meta: { requiresChild: true },
      children: [
        {
          path: 'home',
          name: 'child-home',
          component: () => import('@/views/child/ChildHome.vue'),
          meta: { title: '成长大厅' },
        },
        {
          path: 'challenge',
          name: 'child-challenge',
          component: () => import('@/views/child/ChildChallenge.vue'),
          meta: { title: '挑战' },
        },
        {
          path: 'rewards',
          name: 'child-rewards',
          component: () => import('@/views/child/ChildRewards.vue'),
          meta: { title: '宝箱' },
        },
        {
          path: 'achievements',
          name: 'child-achievements',
          component: () => import('@/views/child/ChildAchievement.vue'),
          meta: { title: '成就图鉴' },
        },
      ],
    },
    {
      path: '/parent',
      component: () => import('@/views/parent/ParentLayout.vue'),
      meta: { requiresParent: true },
      children: [
        {
          path: '',
          redirect: '/parent/dashboard',
        },
        {
          path: 'dashboard',
          name: 'parent-dashboard',
          component: () => import('@/views/parent/ParentDashboard.vue'),
          meta: { title: '数据看板' },
        },
        {
          path: 'scores',
          name: 'parent-scores',
          component: () => import('@/views/parent/ParentScores.vue'),
          meta: { title: '积分记录' },
        },
        {
          path: 'rules',
          name: 'parent-rules',
          component: () => import('@/views/parent/ParentRules.vue'),
          meta: { title: '任务规则' },
        },
        {
          path: 'rewards',
          name: 'parent-rewards',
          component: () => import('@/views/parent/ParentRewards.vue'),
          meta: { title: '奖励商城' },
        },
        {
          path: 'tickets',
          name: 'parent-tickets',
          component: () => import('@/views/parent/ParentTickets.vue'),
          meta: { title: '惊喜奖励券' },
        },
        {
          path: 'shop',
          name: 'parent-shop',
          component: () => import('@/views/parent/ParentShop.vue'),
          meta: { title: '挑战商店' },
        },
        {
          path: 'logs',
          name: 'parent-logs',
          component: () => import('@/views/parent/ParentLogs.vue'),
          meta: { title: '成长日志' },
        },
        {
          path: 'settings',
          name: 'parent-settings',
          component: () => import('@/views/parent/ParentSettings.vue'),
          meta: { title: '家长设置' },
        },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const token = getToken()
  const role = getRole()
  if (to.meta.requiresParent) {
    if (!token || role !== 'parent') {
      return { name: 'login', query: { mode: 'parent' } }
    }
  }
  if (to.meta.requiresChild) {
    if (!token || role !== 'child') {
      return { name: 'login', query: { mode: 'child' } }
    }
  }
  document.title = to.meta.title ? `${to.meta.title} · 我的成长世界` : '我的成长世界'
})

export default router