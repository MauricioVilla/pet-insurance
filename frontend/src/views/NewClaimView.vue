<template>
  <div style="max-width:560px">
    <div class="page-header">
      <h1>New Claim</h1>
      <RouterLink to="/claims" class="btn btn-secondary">← Back</RouterLink>
    </div>
    <div class="card">
      <div v-if="success" class="alert alert-success">
        Claim submitted! It is now being processed.
        <RouterLink to="/claims"> View claims →</RouterLink>
      </div>
      <div v-if="error" class="alert alert-error">{{ error }}</div>

      <div class="form-group">
        <label>Pet</label>
        <select v-model="form.pet" class="form-control">
          <option value="">Select a pet…</option>
          <option v-for="p in pets" :key="p.id" :value="p.id">{{ p.name }} ({{ p.species }})</option>
        </select>
      </div>
      <div class="form-group">
        <label>Invoice File</label>
        <input type="file" class="form-control" @change="onFile" accept=".pdf,.jpg,.jpeg,.png" />
      </div>
      <div class="form-group">
        <label>Invoice Date</label>
        <input v-model="form.invoice_date" type="date" class="form-control" />
      </div>
      <div class="form-group">
        <label>Date of Event</label>
        <input v-model="form.date_of_event" type="date" class="form-control" />
      </div>
      <div class="form-group">
        <label>Amount (USD)</label>
        <input v-model="form.amount" type="number" step="0.01" min="0" class="form-control" />
      </div>
      <button class="btn btn-primary" style="width:100%" :disabled="submitting" @click="submit">
        {{ submitting ? 'Submitting…' : 'Submit Claim' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const pets = ref([])
const form = ref({ pet: '', invoice_date: '', date_of_event: '', amount: '' })
const invoiceFile = ref(null)
const submitting = ref(false)
const error = ref('')
const success = ref(false)

function onFile(e) {
  invoiceFile.value = e.target.files[0]
}

async function submit() {
  submitting.value = true
  error.value = ''
  success.value = false
  try {
    const fd = new FormData()
    fd.append('pet', form.value.pet)
    fd.append('invoice_date', form.value.invoice_date)
    fd.append('date_of_event', form.value.date_of_event)
    fd.append('amount', form.value.amount)
    if (invoiceFile.value) fd.append('invoice', invoiceFile.value)
    await api.post('/claims/', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    success.value = true
    form.value = { pet: '', invoice_date: '', date_of_event: '', amount: '' }
    invoiceFile.value = null
  } catch (e_) {
    const data = e_.response?.data
    error.value = typeof data === 'string' ? data : Object.values(data || {}).flat().join(' ')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  const { data } = await api.get('/pets/')
  pets.value = data.results ?? data
})
</script>
