<template>
  <div>
    <div class="page-header">
      <h1>{{ auth.isCustomer ? 'My Pets' : 'Pets' }}</h1>
      <button v-if="auth.isCustomer" class="btn btn-primary" @click="showModal = true">+ Add Pet</button>
    </div>

    <div v-if="loading" style="text-align:center;padding:2rem;color:#a0aec0">Loading…</div>
    <div v-else-if="pets.length === 0" class="card empty">
      <div class="empty-icon">🐾</div>
      <p>No pets registered yet.</p>
    </div>
    <div v-else class="card" style="padding:0;overflow-x:auto">
      <table style="min-width:700px">
        <thead>
          <tr>
            <th>Name</th>
            <th v-if="auth.canReview">Owner</th>
            <th>Species</th><th>Birth Date</th>
            <th>Status</th><th>Coverage Start</th><th>Coverage End</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="pet in pets" :key="pet.id">
            <td><strong>{{ pet.name }}</strong></td>
            <td v-if="auth.canReview">{{ pet.owner_name || pet.owner_email }}</td>
            <td>{{ pet.species }}</td>
            <td>{{ pet.birth_date }}</td>
            <td><span :class="`badge badge-${pet.status}`">{{ pet.status_display || pet.status }}</span></td>
            <td>{{ pet.coverage_start || '–' }}</td>
            <td>{{ pet.coverage_end || '–' }}</td>
            <td>
              <div style="display:flex;gap:.4rem">
                <button v-if="auth.canReview && pet.status === 'PENDING'" class="btn btn-success btn-sm" :disabled="activating === pet.id" @click="openActivateModal(pet)">
                  ✓ Activate
                </button>
                <template v-if="auth.isCustomer">
                  <button class="btn btn-secondary btn-sm" @click="editPet(pet)">Edit</button>
                  <button class="btn btn-danger btn-sm" @click="openDeleteModal(pet)">Delete</button>
                </template>
              </div>
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
        <div style="display:flex;gap:.75rem;justify-content:flex-end;margin-top:1rem">
          <button class="btn btn-secondary" @click="closeModal">Cancel</button>
          <button class="btn btn-primary" :disabled="saving" @click="savePet">
            {{ saving ? 'Saving…' : 'Save' }}
          </button>
        </div>
      </div>
    </div>
    <!-- Activate Modal -->
    <div class="modal-backdrop" v-if="activateTarget" @click.self="activateTarget = null">
      <div class="modal" style="max-width:400px">
        <div class="modal-header">
          <h2>Activate Coverage</h2>
          <button class="modal-close" @click="activateTarget = null">×</button>
        </div>
        <p style="color:#718096;font-size:.9rem;margin-bottom:1rem">
          Set the coverage start date for <strong>{{ activateTarget?.name }}</strong>.
        </p>
        <div class="form-group">
          <label>Coverage Start</label>
          <input v-model="activateDate" type="date" class="form-control" />
        </div>
        <div style="display:flex;gap:.75rem;justify-content:flex-end">
          <button class="btn btn-secondary" @click="activateTarget = null">Cancel</button>
          <button class="btn btn-success" :disabled="!activateDate || activating" @click="confirmActivate">
            {{ activating ? 'Activating…' : 'Activate' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal-backdrop" v-if="deleteTarget" @click.self="deleteTarget = null">
      <div class="modal" style="max-width:400px;text-align:center">
        <div style="font-size:3rem;margin-bottom:.5rem">⚠️</div>
        <h2 style="font-size:1.15rem;font-weight:700;margin-bottom:.5rem">Delete Pet</h2>
        <p style="color:#718096;font-size:.9rem;margin-bottom:1.5rem">
          Are you sure you want to delete <strong>{{ deleteTarget.name }}</strong>?<br>
          This action cannot be undone.
        </p>
        <div style="display:flex;gap:.75rem;justify-content:center">
          <button class="btn btn-secondary" @click="deleteTarget = null">Cancel</button>
          <button class="btn btn-danger" :disabled="deleting" @click="confirmDelete">
            {{ deleting ? 'Deleting…' : 'Delete' }}
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
const form = ref({ name: '', species: 'DOG', birth_date: '' })
const deleteTarget = ref(null)
const deleting = ref(false)
const activating = ref(null)
const activateTarget = ref(null)
const activateDate = ref('')

async function fetchPets() {
  loading.value = true
  const { data } = await api.get('/pets/')
  pets.value = data.results ?? data
  loading.value = false
}

function editPet(pet) {
  editing.value = pet.id
  form.value = { name: pet.name, species: pet.species, birth_date: pet.birth_date }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editing.value = null
  formError.value = ''
  form.value = { name: '', species: 'DOG', birth_date: '' }
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

function openActivateModal(pet) {
  activateTarget.value = pet
  activateDate.value = new Date().toISOString().slice(0, 10)
}

async function confirmActivate() {
  activating.value = activateTarget.value.id
  try {
    await api.post(`/pets/${activateTarget.value.id}/activate/`, { coverage_start: activateDate.value })
    await fetchPets()
    activateTarget.value = null
  } finally {
    activating.value = null
  }
}

function openDeleteModal(pet) {
  deleteTarget.value = pet
}

async function confirmDelete() {
  deleting.value = true
  try {
    await api.delete(`/pets/${deleteTarget.value.id}/`)
    await fetchPets()
  } finally {
    deleting.value = false
    deleteTarget.value = null
  }
}

onMounted(fetchPets)
</script>
