<script setup>
import { ref, reactive, onMounted } from "vue";
import { usePrimeVue } from "primevue/config";

import Toolbar from "primevue/toolbar";
import Dialog from "primevue/dialog";
import Button from "primevue/button";

import SectionHeaderInfo from "../components/SectionHeaderInfo.vue";
import PercentView from "./PercentView.vue";
import PointView from "./PointView.vue";
import axios from "axios";

const primevue = usePrimeVue();
const languageConfig = primevue.config.locale;

const product = ref({});
const settingsEmitObj = ref();
const deleteProductDialog = ref(false);

let settings = reactive({ percent: {}, point: {} });
const pending = ref(true);

const value = ref(0);
const toolbarSettings = [
  {
    label: "Процентная",
    component: PercentView,
    key: "percent",
  },
  {
    label: "Бальная",
    component: PointView,
    key: "point",
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
  tupayaRuchkaSend();
};

onMounted(() => {
  axios
    .get("http://84.201.143.213:5000/privileges")
    .then((response) => {
      settings.percent = response.data.percent;
      settings.point = response.data.point;
      pending.value = false;
      console.log(settings);
    })
    .catch((error) => {
      console.log(error);
    });
});

const tupayaRuchkaSend = () => {
  axios
    .post("http://84.201.143.213:5000/privileges", {
      settings: settings,
    })
    .then((response) => {
      console.log("SEND NEW PRIVILEGES SETTINGS");
      console.log(response);
    })
    .catch((error) => {
      console.log(error);
    });
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

    <div v-if="!pending">
      <KeepAlive>
        <component
          :is="toolbarSettings[value].component"
          :settingsProps="settings"
          @confirm-delete-privilege="confirmDeletePrivilege($event)"
          @syncrone-settings="tupayaRuchkaSend"
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
