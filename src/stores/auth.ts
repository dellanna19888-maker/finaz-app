import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { supabase, supabaseEnabled } from '../lib/supabase'
import type { User } from '@supabase/supabase-js'

const DEMO_KEY = 'finaz_demo_user'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref('')

  const isLoggedIn = computed(() => !!user.value)
  const email = computed(() => user.value?.email || '')
  const plan = computed(() => (user.value?.user_metadata?.plan as string) || 'free')
  const isPro = computed(() => ['pro', 'business', 'enterprise'].includes(plan.value))

  async function init() {
    if (supabaseEnabled && supabase) {
      const { data } = await supabase.auth.getSession()
      user.value = data.session?.user ?? null
      supabase.auth.onAuthStateChange((_e, s) => { user.value = s?.user ?? null })
    } else {
      const raw = localStorage.getItem(DEMO_KEY)
      if (raw) user.value = JSON.parse(raw)
    }
  }

  async function signUp(email: string, password: string) {
    error.value = ''
    loading.value = true
    try {
      if (supabaseEnabled && supabase) {
        const { error: e } = await supabase.auth.signUp({ email, password })
        if (e) throw e
      } else {
        const demo = { id: crypto.randomUUID(), email, user_metadata: { plan: 'free' } } as unknown as User
        user.value = demo
        localStorage.setItem(DEMO_KEY, JSON.stringify(demo))
      }
    } catch (e: unknown) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function signIn(email: string, password: string) {
    error.value = ''
    loading.value = true
    try {
      if (supabaseEnabled && supabase) {
        const { error: e } = await supabase.auth.signInWithPassword({ email, password })
        if (e) throw e
      } else {
        const demo = { id: crypto.randomUUID(), email, user_metadata: { plan: 'free' } } as unknown as User
        user.value = demo
        localStorage.setItem(DEMO_KEY, JSON.stringify(demo))
      }
    } catch (e: unknown) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function signOut() {
    if (supabaseEnabled && supabase) await supabase.auth.signOut()
    user.value = null
    localStorage.removeItem(DEMO_KEY)
  }

  return { user, loading, error, isLoggedIn, email, plan, isPro, init, signUp, signIn, signOut }
})
