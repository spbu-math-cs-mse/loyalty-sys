<script setup>
import { ref } from "vue";
import { useUserStore } from "@/stores/user";

import Menu from "primevue/menu";
import Button from "primevue/button";
import Drawer from "primevue/drawer";
import Toast from "primevue/toast";
import ToggleButton from "primevue/togglebutton";
import router from "./router";

const user = useUserStore();

let mobileMenuFixed = ref(false);
let desktopMenuFixed = ref(false);

const closeMenu = () => {
  mobileMenuFixed.value = false;
};

const menuItems = ref([
  {
    label: "Статистика",
    icon: "pi pi-chart-line",
    route: "/stats",
    command: () => closeMenu(),
  },
  {
    label: "Привилегии",
    icon: "pi pi-crown",
    route: "/privilege",
    command: () => closeMenu(),
  },
  {
    label: "События",
    icon: "pi pi-calendar-plus",
    route: "/events",
    command: () => closeMenu(),
  },
  {
    label: "Админы",
    icon: "pi pi-shield",
    route: "/admins",
    command: () => closeMenu(),
  },
  {
    label: "Выйти",
    icon: "pi pi-sign-out",
    route: "/login",
    command: () => {
      closeMenu();
      localStorage.removeItem("auth");
      user.auth = false;
      router.push("/login");
    },
  },
]);
</script>

<template>
  <Toast />

  <div v-show="user.auth" class="container lg:hidden">
    <header
      class="header p-3 px-2 lg:px-3 mx-auto my-0 border-round-xs flex justify-content-between lg:block fadeinup animation-ease-out animation-duration-400"
    >
      <div class="">
        <img
          class="block w-2rem"
          src="./assets/logo.png"
          alt="Система лояльности"
        />
      </div>
      <div class="">
        <Button
          icon="pi pi-bars"
          severity="secondary"
          @click="mobileMenuFixed = true"
        />
        <Drawer
          v-model:visible="mobileMenuFixed"
          header="Меню"
          :blockScroll="true"
          :closeButtonProps="{
            severity: 'secondary',
            text: true,
            rounded: false,
          }"
        >
          <Menu :model="menuItems" class="border-none">
            <template #item="{ item, props }">
              <router-link
                v-if="item.route"
                v-slot="{ href, navigate }"
                :to="item.route"
                custom
              >
                <a :href="href" v-bind="props.action" @click="navigate">
                  <span class="text-xl" :class="item.icon" />
                  <span class="ml-2">{{ item.label }}</span>
                </a>
              </router-link>
              <a
                v-else
                :href="item.url"
                :target="item.target"
                v-bind="props.action"
              >
                <span class="text-xl" :class="item.icon" />
                <span class="ml-2">{{ item.label }}</span>
              </a>
            </template>
          </Menu>
        </Drawer>
      </div>
    </header>
  </div>

  <div class="container flex">
    <div v-show="user.auth" :class="{ 'lg:flex': user.auth, hidden: true }">
      <Menu
        :model="menuItems"
        class="aside overflow-scroll sticky p-2 top-0 fadeinleft animation-ease-out animation-duration-400 shadow-1 border-none"
        :class="{ 'min-w-min': !desktopMenuFixed }"
      >
        <template #start>
          <div
            class="flex"
            :class="{
              'pl-2': desktopMenuFixed,
              'justify-content-center': !desktopMenuFixed,
            }"
          >
            <ToggleButton
              v-model="desktopMenuFixed"
              onLabel=" "
              offLabel=" "
              onIcon="pi pi-arrow-left"
              size="small"
              offIcon="pi pi-arrow-right"
              class="toggle__switch"
              aria-label="Do you confirm"
            />
          </div>
          <img
            class="logo block mb-1 mt-2"
            src="./assets/logo.png"
            alt="Система лояльности"
          />
        </template>

        <template #item="{ item, props }">
          <router-link
            v-if="item.route"
            v-slot="{ href, navigate }"
            :to="item.route"
            custom
          >
            <a
              :href="href"
              v-bind="props.action"
              @click="navigate"
              v-tooltip="{ value: desktopMenuFixed ? '' : item.label }"
              :class="{ 'flex justify-content-center': !desktopMenuFixed }"
              class="py-2"
            >
              <span class="text-lg" :class="item.icon" />
              <span v-if="desktopMenuFixed" class="ml-2">{{ item.label }}</span>
            </a>
          </router-link>
          <a
            v-else
            :href="item.url"
            :target="item.target"
            v-bind="props.action"
          >
            <span class="text-lg" :class="item.icon" />
            <span class="ml-2">{{ item.label }}</span>
          </a>
        </template>
      </Menu>
    </div>

    <div class="p-2 w-full">
      <Transition name="fadeIn">
        <router-view />
      </Transition>
    </div>
  </div>
</template>

<style scoped>
.fadeIn-enter-active,
.fadeIn-leave-active {
  transition: all 350ms cubic-bezier(0.665, 1.16, 0.77, 0.985);
}

.fadeIn-enter-from,
.fadeIn-leave-to {
  opacity: 0;
  transform: translateY(5px);
}
</style>
