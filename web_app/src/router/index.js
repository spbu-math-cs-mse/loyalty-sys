import { createRouter, createWebHashHistory } from "vue-router";
import PrivilegeView from "../views/PrivilegeView.vue";

const routes = [
  {
    path: "/",
    name: "home",
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
    path: "/privilege",
    name: "privilege",
    component: () => PrivilegeView,
    meta: {
      title: "Привилегии",
    },
  },
  {
    path: "/events",
    name: "events",
    component: () => import("../views/EventsView.vue"),
    meta: {
      title: "События",
    },
  },
  {
    path: "/admins",
    name: "admins",
    component: () => import("../views/AdminsView.vue"),
    meta: {
      title: "Админы",
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

  if (to.name !== "login" && !auth) {
    next({ name: "login" });
  } else if (to.name === "login" && auth) {
    next({ name: "home" });
  } else {
    next();
    document.title = to.meta.title || "Система лояльности";
  }
});

export default router;
