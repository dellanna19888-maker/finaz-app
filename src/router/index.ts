import { createRouter, createWebHashHistory } from 'vue-router'
import ControlCenter from '../views/ControlCenter.vue'
import Tasks from '../views/Tasks.vue'
import Notes from '../views/Notes.vue'
import Compliance from '../views/Compliance.vue'
import Settings from '../views/Settings.vue'

export default createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', component: ControlCenter },
    { path: '/tasks', component: Tasks },
    { path: '/notes', component: Notes },
    { path: '/compliance', component: Compliance },
    { path: '/settings', component: Settings },
  ],
})
