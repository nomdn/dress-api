import { createRouter, createWebHistory } from 'vue-router';
const Home = () => import('./pages/Home.vue');
const AuthorDetail = () => import('./pages/AuthorDetail.vue');

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
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;