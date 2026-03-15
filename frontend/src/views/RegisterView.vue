<template>
  <div style="max-width:420px;margin:3rem auto">
    <div class="card">
      <h1 style="margin-bottom:1.5rem;font-size:1.4rem">🐾 Create account</h1>
      <div v-if="error" class="alert alert-error">{{ error }}</div>
      <div class="form-group">
        <label>Name</label>
        <input v-model="form.name" type="text" class="form-control" />
      </div>
      <div class="form-group">
        <label>Email</label>
        <input v-model="form.email" type="email" class="form-control" />
      </div>
      <div class="form-group">
        <label>Password</label>
        <input v-model="form.password" type="password" class="form-control" />
      </div>
      <div class="form-group">
        <label>Confirm Password</label>
        <input v-model="form.password_confirm" type="password" class="form-control" />
      </div>
      <button class="btn btn-primary" style="width:100%" :disabled="loading" @click="submit">
        {{ loading ? 'Creating account…' : 'Register' }}
      </button>
      <p style="margin-top:1rem;text-align:center;font-size:.9rem">
        Already have an account? <RouterLink to="/login">Sign in</RouterLink>
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
const form = ref({ name: '', email: '', password: '', password_confirm: '' })
const loading = ref(false)
const error = ref('')

async function submit() {
  loading.value = true
  error.value = ''
  try {
    await auth.register(form.value.name, form.value.email, form.value.password, form.value.password_confirm)
    router.push('/pets')
  } catch (e) {
    const data = e.response?.data
    error.value = typeof data === 'string' ? data : Object.values(data || {}).flat().join(' ')
  } finally {
    loading.value = false
  }
}
</script>
