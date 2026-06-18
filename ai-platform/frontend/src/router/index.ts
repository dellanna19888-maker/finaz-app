import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',          component: () => import('../views/Dashboard.vue') },
    { path: '/chat',      component: () => import('../views/ChatView.vue') },
    { path: '/text',      component: () => import('../views/TextClassifyView.vue') },
    { path: '/image',     component: () => import('../views/ImageClassifyView.vue') },
    { path: '/documents', component: () => import('../views/DocumentsView.vue') },
    { path: '/training',  component: () => import('../views/TrainingView.vue') },
    { path: '/models',    component: () => import('../views/ModelsView.vue') },
  ],
})

export default router
