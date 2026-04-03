import { createRouter, createWebHistory } from 'vue-router';
import Home from './pages/Home.vue';
import AuthorDetail from './pages/AuthorDetail.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/author/:authorname',
    name: 'AuthorDetail',
    component: AuthorDetail,
    props: true
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;