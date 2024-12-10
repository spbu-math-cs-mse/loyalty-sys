import { createRouter, createWebHashHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";

const routes = [
  {
    path: "/",
    name: "home",
    // component: HomeView,
    redirect: { name: "stats" },
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
    path: "/login",
    name: "login",
    component: () => import("../views/LoginView.vue"),
    meta: {
      title: "Вход",
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
  const auth = JSON.parse(localStorage.getItem("auth")) || false;
  console.log(`Перехожу на маршрут: ${to.fullPath}`);
  
  if (to.name !== 'login' && !auth) {
    next({ name: "login" })
  }
  else if (to.name === 'login' && auth) {
    next({ name: "home" })
  }
  else {
    next();
    document.title = to.meta.title || "Система лояльности";
  }
  

});

export default router;
