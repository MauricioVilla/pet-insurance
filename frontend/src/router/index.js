import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const routes = [
  { path: '/', redirect: '/pets' },
  { path: '/login', component: () => import('@/views/LoginView.vue'), meta: { guest: true } },
  { path: '/register', component: () => import('@/views/RegisterView.vue'), meta: { guest: true } },
  { path: '/pets', component: () => import('@/views/PetsView.vue'), meta: { auth: true } },
  { path: '/claims', component: () => import('@/views/ClaimsView.vue'), meta: { auth: true } },
  { path: '/claims/new', component: () => import('@/views/NewClaimView.vue'), meta: { auth: true, role: 'CUSTOMER' } },
  { path: '/review', component: () => import('@/views/ReviewView.vue'), meta: { auth: true, role: 'SUPPORT' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (to.meta.auth && !auth.isAuthenticated) return '/login'
  if (to.meta.guest && auth.isAuthenticated) return '/pets'

  if (auth.isAuthenticated && !auth.user) {
    try { await auth.fetchMe() } catch { auth.logout(); return '/login' }
  }

  if (to.meta.role === 'CUSTOMER' && !auth.isCustomer) return '/claims'
  if (to.meta.role === 'SUPPORT' && !auth.canReview) return '/claims'

  return true
})

export default router
