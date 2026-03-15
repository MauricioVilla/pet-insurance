<template>
  <div>
    <div class="page-header"><h1>Review Queue</h1></div>

    <div v-if="loading" style="text-align:center;padding:2rem;color:#a0aec0">Loading…</div>
    <div v-else-if="claims.length === 0" class="card empty">
      <div class="empty-icon">✅</div>
      <p>No claims pending review.</p>
    </div>
    <div v-else>
      <div class="card" v-for="c in claims" :key="c.id" style="margin-bottom:1rem">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;flex-wrap:wrap">
          <div>
            <div style="font-weight:700;margin-bottom:.3rem">Claim #{{ c.id }} — {{ c.pet?.name }} ({{ c.pet?.species }})</div>
            <div style="font-size:.85rem;color:#718096">
              Amount: <strong>${{ c.amount }}</strong> ·
              Event: {{ c.date_of_event }} ·
              Coverage: {{ c.pet?.coverage_start }} → {{ c.pet?.coverage_end }}
            </div>
            <div style="margin-top:.4rem">
              <span :class="`badge badge-${c.status}`">{{ c.status }}</span>
            </div>
          </div>
          <div style="display:flex;gap:.5rem">
            <button class="btn btn-success btn-sm" :disabled="reviewing === c.id" @click="review(c.id, 'APPROVED', '')">
              ✓ Approve
            </button>
            <button class="btn btn-danger btn-sm" :disabled="reviewing === c.id" @click="openReject(c)">
              ✗ Reject
            </button>
          </div>
        </div>
        <div v-if="c.review_notes" style="margin-top:.5rem;font-size:.85rem;color:#718096">
          Notes: {{ c.review_notes }}
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const claims = ref([])
const loading = ref(true)
const reviewing = ref(null)
const rejectTarget = ref(null)
const rejectNotes = ref('')

async function fetchClaims() {
  loading.value = true
  const { data } = await api.get('/claims/', { params: { status: 'IN_REVIEW' } })
  claims.value = data.results ?? data
  loading.value = false
}

async function review(id, status, notes) {
  reviewing.value = id
  await api.patch(`/claims/${id}/review/`, { status, review_notes: notes })
  await fetchClaims()
  reviewing.value = null
}

function openReject(claim) {
  rejectTarget.value = claim
  rejectNotes.value = ''
}

async function confirmReject() {
  await review(rejectTarget.value.id, 'REJECTED', rejectNotes.value)
  rejectTarget.value = null
}

onMounted(fetchClaims)
</script>
