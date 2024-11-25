import { createRouter, createWebHashHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";

const routes = [
  {
    path: "/",
    name: "home",
    component: HomeView,
    meta: {
      title: "Главная",
    },
  },
  {
    path: "/stats",
    name: "stats",
    component: () => import("../views/StatsView.vue"),
    meta: {
      title: "Cтатистика",
    },
  },
  {
    path: "/coupons",
    name: "coupons",
    component: () => import("../views/CouponsView.vue"),
    meta: {
      title: "Купоны",
    },
  },
  {
    path: "/privilege",
    name: "privilege",
    component: () => import("../views/PrivilegeView.vue"),
    meta: {
      title: "Привилегии",
    },
  },
  {
    path: "/settings",
    name: "settings",
    component: () => import("../views/SettingsView.vue"),
    meta: {
      title: "Настройки",
    },
  },
  {
    path: "/404",
    name: "notfound",
    component: () => import("../views/PageNotFound.vue"),
    meta: {
      title: "404 Страница не найдена",
    },
  },
  {
    path: "/sales",
    name: "sales",
    redirect: { name: "notfound" },
    // component: () => import("../views/SalesView.vue"),
    meta: {
      title: "Скидки",
    },
  },
  {
    path: "/:catchAll(.*)",
    redirect: { name: "notfound" },
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || "Система лояльности";
  next();
});

export default router;
