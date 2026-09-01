import { defineStore } from 'pinia'
import { api, getToken, setToken, clearToken, getRole, setRole } from '@/api'

interface LevelInfo {
  level: number
  level_name: string
  level_icon: string
  description: string
  min_score: number
  lifetime_score: number
  next_level?: number | null
  next_level_name?: string
  next_min_score?: number
  progress: number
}

interface State {
  token: string | null
  isParent: boolean
  isChild: boolean
  child: { id: number; name: string; avatar: string } | null
  balance: number
  level: LevelInfo | null
}

export const useAppStore = defineStore('app', {
  state: (): State => ({
    token: getToken(),
    isParent: getRole() === 'parent',
    isChild: getRole() === 'child',
    child: null,
    balance: 0,
    level: null,
  }),

  getters: {
    isLoggedIn: (s) => !!s.token,
  },

  actions: {
    async login(password: string) {
      const res = await api.login(password)
      this.token = res.access_token
      setToken(res.access_token)
      setRole('parent')
      this.isParent = true
      this.isChild = false
      await this.loadCore()
    },

    async childLogin(password: string) {
      const res = await api.childLogin(password)
      this.token = res.access_token
      setToken(res.access_token)
      setRole('child')
      this.isChild = true
      this.isParent = false
      await this.loadCore()
    },

    async loadCore() {
      const [child, balanceRes] = await Promise.all([
        api.getChild(),
        api.getBalance(),
      ])
      this.child = child
      this.balance = balanceRes.balance
      this.level = balanceRes.level
    },

    async refreshBalance() {
      const res = await api.getBalance()
      this.balance = res.balance
      this.level = res.level
    },

    logout() {
      this.token = null
      this.isParent = false
      this.isChild = false
      clearToken()
    },
  },
})