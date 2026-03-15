<template>
  <div>
    <nav class="navbar" v-if="auth.isAuthenticated">
      <div class="container navbar-inner">
        <span class="navbar-brand">🐾 <span>PetInsure</span></span>
        <div class="navbar-links">
          <RouterLink to="/pets">My Pets</RouterLink>
          <RouterLink to="/claims">Claims</RouterLink>
          <RouterLink v-if="auth.canReview" to="/review">Review Queue</RouterLink>
        </div>
        <div class="navbar-user">
          {{ auth.user?.name || auth.user?.email }}
          <button class="btn btn-secondary btn-sm" style="margin-left:.75rem" @click="logout">Logout</button>
        </div>
      </div>
    </nav>
    <main class="container" style="padding-top:1.5rem">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/store/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>
