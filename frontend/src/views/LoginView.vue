<template>
  <div style="max-width:420px;margin:3rem auto">
    <div class="card">
      <h1 style="margin-bottom:1.5rem;font-size:1.4rem">🐾 Sign in to PetInsure</h1>
      <div v-if="error" class="alert alert-error">{{ error }}</div>
      <div class="form-group">
        <label>Email</label>
        <input v-model="form.email" type="email" class="form-control" placeholder="you@example.com" />
      </div>
      <div class="form-group">
        <label>Password</label>
        <input v-model="form.password" type="password" class="form-control" placeholder="••••••••" />
      </div>
      <button class="btn btn-primary" style="width:100%" :disabled="loading" @click="submit">
        {{ loading ? 'Signing in…' : 'Sign in' }}
      </button>
      <p style="margin-top:1rem;text-align:center;font-size:.9rem">
        Don't have an account? <RouterLink to="/register">Register</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const auth = useAuthStore()
const router = useRouter()
const form = ref({ email: '', password: '' })
const loading = ref(false)
const error = ref('')

async function submit() {
  loading.value = true
  error.value = ''
  try {
    await auth.login(form.value.email, form.value.password)
    router.push('/pets')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Invalid credentials'
  } finally {
    loading.value = false
  }
}
</script>
