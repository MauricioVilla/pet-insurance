<template>
  <div>
    <div class="page-header">
      <h1>Claims</h1>
      <RouterLink v-if="auth.isCustomer" to="/claims/new" class="btn btn-primary">+ New Claim</RouterLink>
    </div>

    <div style="margin-bottom:1rem;display:flex;gap:.75rem;flex-wrap:wrap">
      <select v-model="filter" class="form-control" style="width:auto">
        <option value="">All statuses</option>
        <option v-for="s in statuses" :key="s" :value="s">{{ statusLabels[s] }}</option>
      </select>
    </div>

    <div v-if="loading" style="text-align:center;padding:2rem;color:#a0aec0">Loading…</div>
    <div v-else-if="claims.length === 0" class="card empty">
      <div class="empty-icon">📋</div>
      <p>No claims found.</p>
    </div>
    <div v-else class="card" style="padding:0;overflow:hidden">
      <table>
        <thead>
          <tr>
            <th>Pet</th><th>Amount</th>
            <th>Event Date</th><th>Status</th><th>Notes</th><th>Created</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in claims" :key="c.id">
            <td>{{ c.pet?.name }}</td>
            <td>${{ c.amount }}</td>
            <td>{{ c.date_of_event }}</td>
            <td><span :class="`badge badge-${c.status}`">{{ c.status_display }}</span></td>
            <td style="max-width:200px;white-space:normal;font-size:.8rem;color:#718096">{{ c.review_notes || '–' }}</td>
            <td>{{ new Date(c.created_at).toLocaleDateString() }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/store/auth'

const auth = useAuthStore()
const claims = ref([])
const loading = ref(true)
const filter = ref('')
const statusLabels = {
  SUBMITTED: 'Submitted',
  PROCESSING: 'Processing',
  IN_REVIEW: 'In Review',
  APPROVED: 'Approved',
  REJECTED: 'Rejected'
}
const statuses = Object.keys(statusLabels)

async function fetchClaims() {
  loading.value = true
  const params = filter.value ? { status: filter.value } : {}
  const { data } = await api.get('/claims/', { params })
  claims.value = data.results ?? data
  loading.value = false
}

watch(filter, fetchClaims)
onMounted(fetchClaims)
</script>
