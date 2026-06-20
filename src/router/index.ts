import { createRouter, createWebHashHistory } from 'vue-router'
import Landing from '../views/Landing.vue'
import LoginPage from '../views/LoginPage.vue'
import PricingPage from '../views/PricingPage.vue'
import ControlCenter from '../views/ControlCenter.vue'
import Tasks from '../views/Tasks.vue'
import Channel from '../views/Channel.vue'
import Notes from '../views/Notes.vue'
import Compliance from '../views/Compliance.vue'
import Settings from '../views/Settings.vue'
import SecurityCenter from '../views/SecurityCenter.vue'

export default createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', component: Landing },
    { path: '/login', component: LoginPage },
    { path: '/pricing', component: PricingPage },
    { path: '/app', component: ControlCenter },
    { path: '/tasks', component: Tasks },
    { path: '/channel', component: Channel },
    { path: '/notes', component: Notes },
    { path: '/compliance', component: Compliance },
    { path: '/security', component: SecurityCenter },
    { path: '/settings', component: Settings },
  ],
})
