import { createRouter, createWebHashHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Transactions from '../views/Transactions.vue'
import Budget from '../views/Budget.vue'
import Reports from '../views/Reports.vue'
import Assistant from '../views/Assistant.vue'
import Notes from '../views/Notes.vue'
import Compliance from '../views/Compliance.vue'
import Settings from '../views/Settings.vue'

export default createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', component: Dashboard },
    { path: '/transactions', component: Transactions },
    { path: '/budget', component: Budget },
    { path: '/reports', component: Reports },
    { path: '/assistant', component: Assistant },
    { path: '/notes', component: Notes },
    { path: '/compliance', component: Compliance },
    { path: '/settings', component: Settings },
  ],
})
