<script setup>
import { ref, reactive } from "vue";
import { usePrimeVue } from "primevue/config";

import Toolbar from "primevue/toolbar";
import Dialog from "primevue/dialog";
import Button from "primevue/button";

import SectionHeaderInfo from "../components/SectionHeaderInfo.vue";
import PercentView from "./PercentView.vue";
import PointView from "./PointView.vue";

const primevue = usePrimeVue();
const languageConfig = primevue.config.locale;

const product = ref({});
const settingsEmitObj = ref();
const deleteProductDialog = ref(false);

const settings = reactive({
  percent: {
    settings: {
      active: false,
      levels: 5,
    },
    privileges: [
      {
        id: "AS765HGJAL",
        label: "Бронзовый",
        sale: {
          all: 5,
        },
        starts_from: 0,
      },
      {
        id: "AS76AHGJAL",
        label: "Серебряный",
        sale: {
          all: 15,
        },
        starts_from: 2000,
      },
      {
        id: "BS765HGJAL",
        label: "Золотой",
        sale: {
          all: 25,
        },
        starts_from: 5000,
      },
    ],
  },
  point: {
    settings: {
      active: false,
      levels: 15,
    },
    privileges: [
      {
        id: "1S765HGJAL",
        label: "Уровень 1",
        sale: {
          all: 0.5,
        },
        saleAll: 0.5,
        starts_from: 0,
      },
    ],
  },
});

const value = ref(0);
const toolbarSettings = [
  {
    label: "Процентная",
    component: PercentView,
    props: settings.percent,
  },
  {
    label: "Бальная",
    component: PointView,
    props: settings.point,
  },
];

const confirmDeletePrivilege = (data) => {
  product.value = data[1];
  settingsEmitObj.value = data[0];
  deleteProductDialog.value = true;
};

const deletePrivilege = () => {
  settings[settingsEmitObj.value].privileges = settings[
    settingsEmitObj.value
  ].privileges.filter((items) => items.label !== product.value.label);
  deleteProductDialog.value = false;
};
</script>

<template>
  <div class="privilege container__wrapper lg:py-4 py-1 md:pl-3 pl-0">
    <SectionHeaderInfo title="Привилегии" />

    <Toolbar class="mb-4 border-none shadow-1">
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

    <div>
      <KeepAlive>
        <component
          :is="toolbarSettings[value].component"
          :settingsProps="toolbarSettings[value].props"
          @confirm-delete-privilege="confirmDeletePrivilege($event)"
          class="mt-0 settings__component"
        />
      </KeepAlive>
    </div>

    <Dialog
      v-model:visible="deleteProductDialog"
      :style="{ width: '450px' }"
      :header="languageConfig.deleteTitle"
      :modal="true"
    >
      <div class="flex items-center gap-4">
        <i class="pi pi-exclamation-triangle !text-3xl" />
        <span v-if="product"
          >Уверены, что хотите удалить <b>{{ product.label }}</b
          >?</span
        >
      </div>
      <template #footer>
        <Button
          :label="languageConfig.reject"
          icon="pi pi-times"
          text
          @click="deleteProductDialog = false"
        />
        <Button
          :label="languageConfig.accept"
          icon="pi pi-check"
          @click="deletePrivilege"
        />
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.settings__component :deep(.settings__title) {
  color: var(--p-text-color);
}

.settings__component :deep(.p-inputtext) {
  max-width: 6rem;
}

@media screen and (max-width: 767px) {
  .settings__component :deep(.switch) {
    transform: scale(0.9);
  }

  .settings__component :deep(.p-inputtext) {
    font-size: 0.85rem;
  }
}
</style>
