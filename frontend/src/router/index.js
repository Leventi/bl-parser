import { createWebHistory, createRouter } from "vue-router";
import Home from "@/views/HomePage.vue";
import About from "@/views/AboutPage.vue";
import NotFound from "@/views/NotFound.vue";
import Monopoly from "@/views/MonopolyCheck.vue";

const routes = [
  {
    path: "/",
    name: "Home Page",
    component: Home,
  },
  {
    path: "/about",
    name: "About Page",
    component: About,
  },
  {
    path: "/monopoly_check/:inn",
    name: "Monopoly Check",
    component: Monopoly,
  },
  {
    path: "/:catchAll(.*)",
    component: NotFound,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;