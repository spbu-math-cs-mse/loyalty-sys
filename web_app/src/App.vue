<script setup>
import Menu from "primevue/menu";
import Button from "primevue/button";
import Drawer from "primevue/drawer";
import Toast from "primevue/toast";
import ToggleSwitch from "primevue/toggleswitch";

import { computed, onMounted, onUnmounted, ref } from "vue";

let mobileMenuFixed = ref(false);
let desktopMenuFixed = ref(false);

const menuExpandWidth = 992;

const closeMenu = () => {
  mobileMenuFixed.value = false;
};

const menuItems = ref([
  {
    label: "Статистика",
    icon: "pi pi-chart-bar",
    route: "/stats",
    command: () => closeMenu(),
  },
  {
    label: "Привилегии",
    icon: "pi pi-user-plus",
    route: "/privilege",
    command: () => closeMenu(),
  },
  // Allowed comments, will be needed later
  // {
  //   label: "Настройки",
  //   icon: "pi pi-cog",
  //   route: "/settings",
  //   command: () => closeMenu(),
  // },
  // {
  //   label: "Купоны",
  //   icon: "pi pi-tag",
  //   route: "/coupons",
  //   command: () => closeMenu(),
  // },
  // {
  //   label: "Скидки",
  //   icon: "pi pi-percentage",
  //   route: "/sales",
  //   command: () => closeMenu(),
  // },
]);

const useBreakpoints = () => {
  let windowWidth = ref(window.innerWidth);
  let windowHeight = ref(window.innerHeight);

  const onWidthChange = () => {
    windowWidth.value = window.innerWidth;
    windowHeight.value = window.innerHeight;
  };

  onMounted(() => window.addEventListener("resize", onWidthChange));
  onUnmounted(() => window.removeEventListener("resize", onWidthChange));

  const width = computed(() => windowWidth.value);
  const height = computed(() => windowHeight.value);

  return { width, height };
};

const { width, height } = useBreakpoints();
</script>

<template>
  <Toast />
  <div v-if="width < menuExpandWidth" class="container">
    <header
      class="header p-3 px-2 lg:px-3 mx-auto my-0 border-round-xs flex justify-content-between lg:block"
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
    <Menu
      v-if="width >= menuExpandWidth"
      :model="menuItems"
      class="aside overflow-scroll sticky p-2 top-0 fadeinleft animation-ease-out animation-duration-400 shadow-1 border-none"
      :class="{ 'min-w-min': !desktopMenuFixed }"
    >
      <template #start>
        <div
          v-if="width >= menuExpandWidth"
          class="flex"
          :class="{
            'pl-2': desktopMenuFixed,
            'justify-content-center': !desktopMenuFixed,
          }"
        >
          <ToggleSwitch v-model="desktopMenuFixed" class="toggle__switch">
            <template #handle="{ checked }">
              <i
                :class="[
                  'text-xs pi',
                  { 'pi-lock': checked, 'pi-lock-open': !checked },
                ]"
              />
            </template>
          </ToggleSwitch>
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
        <a v-else :href="item.url" :target="item.target" v-bind="props.action">
          <span class="text-lg" :class="item.icon" />
          <span class="ml-2">{{ item.label }}</span>
        </a>
      </template>
    </Menu>

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
