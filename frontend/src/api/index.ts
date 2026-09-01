/**
 * API 请求封装
 */
/**
 * API 请求封装
 */
const BASE = '/api'

const TOKEN_KEY = 'gw_token'
const ROLE_KEY = 'gw_role'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(ROLE_KEY)
}

export function getRole(): 'parent' | 'child' | null {
  return (localStorage.getItem(ROLE_KEY) as 'parent' | 'child') || null
}

export function setRole(role: 'parent' | 'child') {
  localStorage.setItem(ROLE_KEY, role)
}

export async function request<T = any>(
  path: string,
  options: { method?: string; body?: any; auth?: boolean } = {},
): Promise<T> {
  const { method = 'GET', body, auth = true } = options
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (auth) {
    const token = getToken()
    if (token) headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })

  if (!res.ok) {
    let msg = `请求失败(${res.status})`
    try {
      const data = await res.json()
      msg = data.detail || msg
    } catch {
      /* ignore */
    }
    throw new Error(msg)
  }

  return res.json() as Promise<T>
}

export const api = {
  // 认证
  login: (password: string) => request('/auth/login', { method: 'POST', body: { password }, auth: false }),
  childLogin: (password: string) => request('/auth/child-login', { method: 'POST', body: { password }, auth: false }),
  // 孩子
  getChild: () => request('/child'),
  // 任务
  getTasks: () => request('/tasks'),
  createTask: (body: any) => request('/tasks', { method: 'POST', body }),
  updateTask: (id: number, body: any) => request(`/tasks/${id}`, { method: 'PUT', body }),
  deleteTask: (id: number) => request(`/tasks/${id}`, { method: 'DELETE' }),
  // 积分
  addScore: (body: any) => request('/scores', { method: 'POST', body }),
  getBalance: () => request('/scores/balance'),
  getHistory: (limit = 50) => request(`/scores/history?limit=${limit}`),
  getDashboard: (days = 14) => request(`/scores/dashboard?days=${days}`),
  // 等级
  getLevels: () => request('/levels'),
  getLevelProgress: () => request('/levels/progress'),
  // 成就
  getAchievements: () => request('/achievements'),
  // 奖励
  getRewards: () => request('/rewards'),
  createReward: (body: any) => request('/rewards', { method: 'POST', body }),
  updateReward: (id: number, body: any) => request(`/rewards/${id}`, { method: 'PUT', body }),
  deleteReward: (id: number) => request(`/rewards/${id}`, { method: 'DELETE' }),
  exchange: (body: any) => request('/rewards/exchange', { method: 'POST', body }),
  getExchangeHistory: () => request('/rewards/history'),
  // 日志
  getLogs: (limit = 50) => request(`/logs?limit=${limit}`),
  createLog: (body: any) => request('/logs', { method: 'POST', body }),
  deleteLog: (id: number) => request(`/logs/${id}`, { method: 'DELETE' }),
  // 每日打卡
  getCheckinToday: () => request('/checkin/today'),
  requestCheckin: (taskRuleId: number) => request(`/checkin/request?task_rule_id=${taskRuleId}`, { method: 'POST' }),
  confirmCheckin: (checkinId: number) => request(`/checkin/confirm/${checkinId}`, { method: 'POST' }),
  getPendingCheckins: () => request('/checkin/pending'),
  getCheckinHistory: (days = 30) => request(`/checkin/history?days=${days}`),
  // 个人目标
  getGoals: () => request('/goals'),
  createGoal: (body: any) => request('/goals', { method: 'POST', body }),
  approveGoal: (id: number) => request(`/goals/${id}/approve`, { method: 'PUT' }),
  rejectGoal: (id: number) => request(`/goals/${id}/reject`, { method: 'PUT' }),
  deleteGoal: (id: number) => request(`/goals/${id}`, { method: 'DELETE' }),
  // 宝石银行
  getBank: () => request('/bank'),
  deposit: (amount: number) => request(`/bank/deposit?amount=${amount}`, { method: 'POST' }),
  withdraw: (amount: number) => request(`/bank/withdraw?amount=${amount}`, { method: 'POST' }),
  // 惊喜奖励券
  getTickets: () => request('/tickets'),
  createTicket: (body: any) => request('/tickets', { method: 'POST', body }),
  updateTicket: (id: number, body: any) => request(`/tickets/${id}`, { method: 'PUT', body }),
  deleteTicket: (id: number) => request(`/tickets/${id}`, { method: 'DELETE' }),
  purchaseTicket: (id: number) => request(`/tickets/${id}/purchase`, { method: 'POST' }),
  useTicket: (id: number) => request(`/tickets/${id}/use`, { method: 'POST' }),
  // 家长配置
  getParentConfig: () => request('/parent/config'),
  updateParentConfig: (body: any) => request('/parent/config', { method: 'PUT', body }),
  // 成长简报
  getWeeklyReport: (weeksAgo = 0) => request(`/report/weekly?weeks_ago=${weeksAgo}`),
  // 亲子任务商店
  getShopTasks: () => request('/shop'),
  createShopTask: (body: any) => request('/shop', { method: 'POST', body }),
  updateShopTask: (id: number, body: any) => request(`/shop/${id}`, { method: 'PUT', body }),
  deleteShopTask: (id: number) => request(`/shop/${id}`, { method: 'DELETE' }),
  acceptShopTask: (id: number) => request(`/shop/${id}/accept`, { method: 'POST' }),
  submitShopTask: (id: number) => request(`/shop/${id}/submit`, { method: 'POST' }),
  confirmShopTask: (id: number) => request(`/shop/${id}/confirm`, { method: 'POST' }),
  rejectShopTask: (id: number) => request(`/shop/${id}/reject`, { method: 'POST' }),
  cancelShopTask: (id: number) => request(`/shop/${id}/cancel`, { method: 'POST' }),
  // 数据管理
  exportData: () => request('/data/export'),
  importData: (data: any) => request('/data/import', { method: 'POST', body: { data } }),
  clearData: () => request('/data/clear', { method: 'POST', body: { confirm: true } }),
}