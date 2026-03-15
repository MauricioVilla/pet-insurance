<template>
  <div>
    <div class="page-header">
      <h1>My Pets</h1>
      <button v-if="auth.isCustomer" class="btn btn-primary" @click="showModal = true">+ Add Pet</button>
    </div>

    <div v-if="loading" style="text-align:center;padding:2rem;color:#a0aec0">Loading…</div>
    <div v-else-if="pets.length === 0" class="card empty">
      <div class="empty-icon">🐾</div>
      <p>No pets registered yet.</p>
    </div>
    <div v-else class="card" style="padding:0;overflow:hidden">
      <table>
        <thead>
          <tr>
            <th>Name</th><th>Species</th><th>Birth Date</th>
            <th>Coverage Start</th><th>Coverage End</th><th v-if="auth.isCustomer">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="pet in pets" :key="pet.id">
            <td><strong>{{ pet.name }}</strong></td>
            <td>{{ pet.species }}</td>
            <td>{{ pet.birth_date }}</td>
            <td>{{ pet.coverage_start }}</td>
            <td>{{ pet.coverage_end }}</td>
            <td v-if="auth.isCustomer">
              <button class="btn btn-secondary btn-sm" @click="editPet(pet)">Edit</button>
              <button class="btn btn-danger btn-sm" style="margin-left:.4rem" @click="deletePet(pet.id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add/Edit Modal -->
    <div class="modal-backdrop" v-if="showModal" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ editing ? 'Edit Pet' : 'Add Pet' }}</h2>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        <div v-if="formError" class="alert alert-error">{{ formError }}</div>
        <div class="form-group">
          <label>Name</label>
          <input v-model="form.name" class="form-control" />
        </div>
        <div class="form-group">
          <label>Species</label>
          <select v-model="form.species" class="form-control">
            <option value="DOG">Dog</option>
            <option value="CAT">Cat</option>
            <option value="OTHER">Other</option>
          </select>
        </div>
        <div class="form-group">
          <label>Birth Date</label>
          <input v-model="form.birth_date" type="date" class="form-control" />
        </div>
        <div class="form-group">
          <label>Coverage Start</label>
          <input v-model="form.coverage_start" type="date" class="form-control" />
        </div>
        <div style="display:flex;gap:.75rem;justify-content:flex-end;margin-top:1rem">
          <button class="btn btn-secondary" @click="closeModal">Cancel</button>
          <button class="btn btn-primary" :disabled="saving" @click="savePet">
            {{ saving ? 'Saving…' : 'Save' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/store/auth'

const auth = useAuthStore()
const pets = ref([])
const loading = ref(true)
const showModal = ref(false)
const editing = ref(null)
const saving = ref(false)
const formError = ref('')
const form = ref({ name: '', species: 'DOG', birth_date: '', coverage_start: '' })

async function fetchPets() {
  loading.value = true
  const { data } = await api.get('/pets/')
  pets.value = data.results ?? data
  loading.value = false
}

function editPet(pet) {
  editing.value = pet.id
  form.value = { name: pet.name, species: pet.species, birth_date: pet.birth_date, coverage_start: pet.coverage_start }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editing.value = null
  formError.value = ''
  form.value = { name: '', species: 'DOG', birth_date: '', coverage_start: '' }
}

async function savePet() {
  saving.value = true
  formError.value = ''
  try {
    if (editing.value) {
      await api.put(`/pets/${editing.value}/`, form.value)
    } else {
      await api.post('/pets/', form.value)
    }
    await fetchPets()
    closeModal()
  } catch (e) {
    const data = e.response?.data
    formError.value = typeof data === 'string' ? data : Object.values(data || {}).flat().join(' ')
  } finally {
    saving.value = false
  }
}

async function deletePet(id) {
  if (!confirm('Delete this pet?')) return
  await api.delete(`/pets/${id}/`)
  await fetchPets()
}

onMounted(fetchPets)
</script>
