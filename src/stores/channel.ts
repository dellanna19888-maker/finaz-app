import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export interface ChannelProfile {
  platform: string
  handle: string
  followers: number
  niche: string
  recent: string // letzte Inhalte (Titel/Notizen), Freitext
}

export interface Competitor {
  id: string
  handle: string
  followers: number
  notes: string // was sie posten / Auffälligkeiten
}

const P_KEY = 'finaz_channel'
const C_KEY = 'finaz_competitors'

function loadProfile(): ChannelProfile {
  const base: ChannelProfile = { platform: 'YouTube', handle: '', followers: 0, niche: '', recent: '' }
  try {
    const d = localStorage.getItem(P_KEY)
    if (d) return { ...base, ...(JSON.parse(d) as Partial<ChannelProfile>) }
  } catch {
    /* ignore */
  }
  return base
}

function loadCompetitors(): Competitor[] {
  try {
    const d = localStorage.getItem(C_KEY)
    if (d) {
      const a = JSON.parse(d) as unknown
      if (Array.isArray(a)) return a as Competitor[]
    }
  } catch {
    /* ignore */
  }
  return []
}

export const useChannelStore = defineStore('channel', () => {
  const profile = ref<ChannelProfile>(loadProfile())
  const competitors = ref<Competitor[]>(loadCompetitors())

  watch(profile, () => localStorage.setItem(P_KEY, JSON.stringify(profile.value)), { deep: true })
  watch(competitors, () => localStorage.setItem(C_KEY, JSON.stringify(competitors.value)), { deep: true })

  function addCompetitor(c?: Partial<Competitor>) {
    competitors.value.push({
      id: Date.now().toString(),
      handle: c?.handle ?? '',
      followers: c?.followers ?? 0,
      notes: c?.notes ?? '',
    })
  }

  function deleteCompetitor(id: string) {
    competitors.value = competitors.value.filter((x) => x.id !== id)
  }

  return { profile, competitors, addCompetitor, deleteCompetitor }
})
