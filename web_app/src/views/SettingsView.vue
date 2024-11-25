<script setup>
import { ref } from "vue";
import { useToast } from "primevue/usetoast";
import { usePrimeVue } from "primevue/config";

import Toolbar from "primevue/toolbar";
import Button from "primevue/button";

import SectionHeaderInfo from "../components/SectionHeaderInfo.vue";
import PercentView from "./PercentView.vue";
import PointView from "./PointView.vue";

const toolbarSettings = ref([
  {
    label: "Процентная",
    component: PercentView,
  },
  {
    label: "Бальная",
    component: PointView,
  },
]);

const value = ref(0);
const toast = useToast();
const primevue = usePrimeVue();
const languageConfig = primevue.config.locale;
const toastConfig = languageConfig.toast;

function deepEqual(first, second) {
  if (first === second) return true;

  if (
    typeof first !== "object" ||
    first === null ||
    typeof second !== "object" ||
    second === null
  ) {
    return false;
  }

  const keysFirst = Object.keys(first);
  const keysSecond = Object.keys(second);

  if (keysFirst.length !== keysSecond.length) return false;

  return keysFirst.every((key) => {
    return keysSecond.includes(key) && deepEqual(first[key], second[key]);
  });
}
</script>

<template>
  <div class="privilege lg:py-4 py-1 md:pl-3 pl-0">
    <SectionHeaderInfo title="Настройки" />

    <Toolbar>
      <template #start>
        <Button
          v-for="(btn, index) in toolbarSettings"
          :label="btn.label"
          class="mr-2"
          @click="value = index"
          :outlined="value !== index"
        />
      </template>
    </Toolbar>

    <div class="p-3 px-2 md:px-3">
      <KeepAlive>
        <component
          :is="toolbarSettings[value].component"
          class="mt-1 settings__component"
        />
      </KeepAlive>
    </div>
  </div>
</template>

<style scoped>
.settings__component /deep/ .settings__title {
  color: var(--p-text-color);
}
.settings__component /deep/ .p-inputtext {
  max-width: 6rem;
}
</style>
