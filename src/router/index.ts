import { createRouter, createWebHashHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Transactions from '../views/Transactions.vue'
import Budget from '../views/Budget.vue'
import Reports from '../views/Reports.vue'

export default createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', component: Dashboard },
    { path: '/transactions', component: Transactions },
    { path: '/budget', component: Budget },
    { path: '/reports', component: Reports },
  ],
})
