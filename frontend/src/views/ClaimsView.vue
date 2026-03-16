<template>
  <div>
    <div class="page-header">
      <h1>Claims</h1>
      <RouterLink v-if="auth.isCustomer" to="/claims/new" class="btn btn-primary">+ New Claim</RouterLink>
    </div>

    <div class="tabs">
      <button :class="['tab', { active: filter === '' }]" @click="filter = ''">All</button>
      <button v-for="s in statuses" :key="s" :class="['tab', { active: filter === s }]" @click="filter = s">
        {{ statusLabels[s] }}
      </button>
    </div>

    <div v-if="loading" style="text-align:center;padding:2rem;color:#a0aec0">Loading…</div>
    <div v-else-if="filteredClaims.length === 0" class="card empty">
      <div class="empty-icon">📋</div>
      <p>No claims found.</p>
    </div>
    <div v-else class="card" style="padding:0;overflow-x:auto">
      <table style="min-width:800px">
        <thead>
          <tr>
            <th>Pet</th><th v-if="auth.canReview">Owner</th><th>Amount</th>
            <th>Event Date</th><th>Invoice</th><th>Status</th><th>Notes</th><th>Created</th>
            <th v-if="auth.canReview">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in filteredClaims" :key="c.id">
            <td>{{ c.pet?.name }}</td>
            <td v-if="auth.canReview">{{ c.owner_name || c.owner_email }}</td>
            <td>${{ c.amount }}</td>
            <td>{{ c.date_of_event }}</td>
            <td>
              <button class="btn btn-secondary btn-sm" @click="openInvoice(c)">📄 View</button>
            </td>
            <td><span :class="`badge badge-${c.status}`">{{ c.status_display }}</span></td>
            <td style="font-size:.8rem;color:#718096;white-space:nowrap">
              <template v-if="!c.review_notes">–</template>
              <template v-else-if="c.review_notes.length <= 27">{{ c.review_notes }}</template>
              <template v-else>
                {{ c.review_notes.slice(0, 27) }}…
                <a href="#" style="color:#5a67d8;margin-left:.25rem" @click.prevent="notesTarget = c">see more</a>
              </template>
            </td>
            <td>{{ new Date(c.created_at).toLocaleDateString() }}</td>
            <td v-if="auth.canReview">
              <div v-if="c.status === 'IN_REVIEW'" style="display:flex;gap:.4rem">
                <button class="btn btn-success btn-sm" :disabled="reviewing === c.id" @click="openApprove(c)">
                  ✓ Approve
                </button>
                <button class="btn btn-danger btn-sm" :disabled="reviewing === c.id" @click="openReject(c)">
                  ✗ Reject
                </button>
              </div>
              <span v-else style="color:#a0aec0;font-size:.8rem">–</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Approve modal -->
    <div class="modal-backdrop" v-if="approveTarget" @click.self="approveTarget = null">
      <div class="modal">
        <div class="modal-header">
          <h2>Approve Claim #{{ approveTarget?.id }}</h2>
          <button class="modal-close" @click="approveTarget = null">×</button>
        </div>
        <div class="form-group">
          <label>Observations (optional)</label>
          <textarea v-model="approveNotes" class="form-control" rows="3" placeholder="Add any observations…"></textarea>
        </div>
        <div style="display:flex;gap:.75rem;justify-content:flex-end">
          <button class="btn btn-secondary" @click="approveTarget = null">Cancel</button>
          <button class="btn btn-success" @click="confirmApprove">Approve</button>
        </div>
      </div>
    </div>

    <!-- Reject modal -->
    <div class="modal-backdrop" v-if="rejectTarget" @click.self="rejectTarget = null">
      <div class="modal">
        <div class="modal-header">
          <h2>Reject Claim #{{ rejectTarget?.id }}</h2>
          <button class="modal-close" @click="rejectTarget = null">×</button>
        </div>
        <div class="form-group">
          <label>Reason (required)</label>
          <textarea v-model="rejectNotes" class="form-control" rows="3" placeholder="Explain why this claim is being rejected…"></textarea>
        </div>
        <div style="display:flex;gap:.75rem;justify-content:flex-end">
          <button class="btn btn-secondary" @click="rejectTarget = null">Cancel</button>
          <button class="btn btn-danger" :disabled="!rejectNotes.trim()" @click="confirmReject">Reject</button>
        </div>
      </div>
    </div>

    <!-- Invoice preview modal -->
    <div class="modal-backdrop" v-if="invoiceTarget" @click.self="invoiceTarget = null">
      <div class="modal" style="max-width:700px;max-height:90vh;display:flex;flex-direction:column">
        <div class="modal-header">
          <h2>Invoice — Claim #{{ invoiceTarget?.id }}</h2>
          <button class="modal-close" @click="invoiceTarget = null">×</button>
        </div>
        <div style="flex:1;overflow:auto;text-align:center;min-height:300px">
          <img
            v-if="isImage(invoiceTarget.invoice)"
            :src="invoiceUrl(invoiceTarget.invoice)"
            style="max-width:100%;border-radius:6px"
            alt="Invoice"
          />
          <object
            v-else-if="isPdf(invoiceTarget.invoice)"
            :data="invoiceUrl(invoiceTarget.invoice)"
            type="application/pdf"
            style="width:100%;height:500px;border:none;border-radius:6px"
          >
            <p style="padding:2rem;color:#718096">Cannot preview PDF in browser.</p>
          </object>
          <div v-else style="padding:2rem;color:#718096">
            <p>Preview not available for this file type.</p>
          </div>
          <a :href="invoiceUrl(invoiceTarget.invoice)" target="_blank" class="btn btn-secondary btn-sm" style="margin-top:.75rem;display:inline-block">
            Open in new tab ↗
          </a>
        </div>
      </div>
    </div>
    <!-- Notes modal -->
    <div class="modal-backdrop" v-if="notesTarget" @click.self="notesTarget = null">
      <div class="modal">
        <div class="modal-header">
          <h2>Notes — Claim #{{ notesTarget?.id }}</h2>
          <button class="modal-close" @click="notesTarget = null">×</button>
        </div>
        <p style="white-space:pre-wrap;color:#4a5568;font-size:.9rem">{{ notesTarget?.review_notes }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/store/auth'

const auth = useAuthStore()
const allClaims = ref([])
const loading = ref(true)
const filter = ref('')
const reviewing = ref(null)
const rejectTarget = ref(null)
const rejectNotes = ref('')
const approveTarget = ref(null)
const approveNotes = ref('')
const invoiceTarget = ref(null)
const notesTarget = ref(null)
const statusLabels = {
  SUBMITTED: 'Submitted',
  PROCESSING: 'Processing',
  IN_REVIEW: 'In Review',
  APPROVED: 'Approved',
  REJECTED: 'Rejected'
}
const statuses = Object.keys(statusLabels)

const filteredClaims = computed(() => {
  if (!filter.value) return allClaims.value
  return allClaims.value.filter(c => c.status === filter.value)
})

async function fetchClaims() {
  loading.value = true
  const { data } = await api.get('/claims/')
  allClaims.value = data.results ?? data
  loading.value = false
}

async function reviewClaim(id, status, notes) {
  reviewing.value = id
  await api.patch(`/claims/${id}/review/`, { status, review_notes: notes })
  await fetchClaims()
  reviewing.value = null
}

function openReject(claim) {
  rejectTarget.value = claim
  rejectNotes.value = ''
}

function openApprove(claim) {
  approveTarget.value = claim
  approveNotes.value = ''
}

async function confirmApprove() {
  await reviewClaim(approveTarget.value.id, 'APPROVED', approveNotes.value)
  approveTarget.value = null
}

function openInvoice(claim) {
  invoiceTarget.value = claim
}

function invoiceUrl(url) {
  if (!url) return ''
  try {
    const u = new URL(url)
    return u.pathname
  } catch {
    return url
  }
}

function isImage(url) {
  return /\.(jpe?g|png|gif|webp)/i.test(url)
}

function isPdf(url) {
  return /\.pdf/i.test(url)
}

async function confirmReject() {
  await reviewClaim(rejectTarget.value.id, 'REJECTED', rejectNotes.value)
  rejectTarget.value = null
}

onMounted(fetchClaims)
</script>
