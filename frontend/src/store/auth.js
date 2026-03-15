import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token'))

  const isAuthenticated = computed(() => !!accessToken.value)
  const isCustomer = computed(() => user.value?.role === 'CUSTOMER')
  const isSupport = computed(() => user.value?.role === 'SUPPORT')
  const isAdmin = computed(() => user.value?.role === 'ADMIN')
  const canReview = computed(() => isSupport.value || isAdmin.value)

  async function login(email, password) {
    const { data } = await api.post('/auth/login/', { email, password })
    accessToken.value = data.access
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    await fetchMe()
  }

  async function register(name, email, password, passwordConfirm) {
    await api.post('/auth/register/', {
      name, email, password, password_confirm: passwordConfirm
    })
    await login(email, password)
  }

  async function fetchMe() {
    const { data } = await api.get('/auth/me/')
    user.value = data
  }

  function logout() {
    user.value = null
    accessToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return { user, accessToken, isAuthenticated, isCustomer, isSupport, isAdmin, canReview, login, register, fetchMe, logout }
})
