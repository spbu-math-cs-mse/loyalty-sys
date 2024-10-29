import { createRouter, createWebHashHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";

const routes = [
  {
    path: "/",
    name: "home",
    component: HomeView,
  },
  {
    path: "/stats",
    name: "stats",
    component: () => import("../views/StatsView.vue"),
  },
  {
    path: "/coupons",
    name: "coupons",
    component: () => import("../views/CouponsView.vue"),
  },
  {
    path: "/privilege",
    name: "privilege",
    component: () => import("../views/PrivilegeView.vue"),
  },
  {
    path: "/404",
    name: "notfound",
    component: () => import("../views/PageNotFound.vue"),
  },
  {
    path: "/sales",
    name: "sales",
    redirect: { name: "notfound" },
    // component: () => import("../views/SalesView.vue"),
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

export default router;
