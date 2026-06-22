import { createRouter, createWebHashHistory } from 'vue-router'
import ControlCenter from '../views/ControlCenter.vue'
import Tasks from '../views/Tasks.vue'
import Channel from '../views/Channel.vue'
import Finance from '../views/Finance.vue'
import Notes from '../views/Notes.vue'
import Compliance from '../views/Compliance.vue'
import Settings from '../views/Settings.vue'

export default createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', component: ControlCenter },
    { path: '/tasks', component: Tasks },
    { path: '/channel', component: Channel },
    { path: '/finance', component: Finance },
    { path: '/notes', component: Notes },
    { path: '/compliance', component: Compliance },
    { path: '/settings', component: Settings },
  ],
})
