<script setup>
import { ref, watch, reactive, computed } from "vue";
import { usePrimeVue } from "primevue/config";
import { useToast } from "primevue/usetoast";
import { deepEqual } from "@/settings";

import ToggleSwitch from "primevue/toggleswitch";
import InputNumber from "primevue/inputnumber";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import Tabs from "primevue/tabs";
import TabList from "primevue/tablist";
import Tab from "primevue/tab";
import TabPanels from "primevue/tabpanels";
import TabPanel from "primevue/tabpanel";
import Toolbar from "primevue/toolbar";
import Badge from "primevue/badge";
import Dialog from "primevue/dialog";

const props = defineProps({
  settingsProps: {
    type: Object,
    required: true,
  },
});

const toast = useToast();
const primevue = usePrimeVue();
const languageConfig = primevue.config.locale;
const toastConfig = languageConfig.toast;

const product = ref({});
const productDialog = ref(false);
const submitted = ref(false);
const productDialogText = ref();

const privilegeLevels = ref(props.settingsProps.privileges);
const settings = ref(props.settingsProps.settings);

const editableSettings = reactive({ ...props.settingsProps.settings });

const isModified = computed(() => {
  return deepEqual(settings.value, editableSettings);
});

const saveSettings = () => {
  Object.assign(settings.value, editableSettings);
};

const cancelSettingsChanges = () => {
  Object.assign(editableSettings, settings.value);
};

const createId = () => {
  let id = "";
  var chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  for (var i = 0; i < 10; i++) {
    id += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return id;
};

const openNew = () => {
  productDialogText.value = languageConfig.addTitle;
  product.value = {};
  submitted.value = false;
  productDialog.value = true;
};

const hideDialog = () => {
  productDialog.value = false;
  submitted.value = false;
};

const saveProduct = () => {
  submitted.value = true;

  if (product?.value.label?.trim()) {
    if (product.value.id) {
      const index = privilegeLevels.value.findIndex(
        (privilege) => privilege.id === product.value.id
      );
      privilegeLevels.value[index] = product.value;
      toast.add({
        severity: toastConfig.severity.success,
        summary: toastConfig.summary.successTitle,
        detail: toastConfig.detail.privillege.edit,
        life: 3000,
      });
    } else {
      product.value.id = createId();
      privilegeLevels.value.push(product.value);
      toast.add({
        severity: toastConfig.severity.success,
        summary: toastConfig.summary.success,
        detail: toastConfig.detail.privillege.add,
        life: 3000,
      });
    }

    productDialog.value = false;
    product.value = {};
  }
};

const editPrivilege = (privilege) => {
  productDialogText.value = languageConfig.editTitle;
  product.value = { ...privilege };
  productDialog.value = true;
};

watch(
  () => props.settingsProps,
  (newSettingsProps, oldSettingsProps) => {
    privilegeLevels.value = newSettingsProps.privileges;
    settings.value = newSettingsProps.settings;
  },
  { deep: true }
);
</script>

<template>
  <div class="">
    <Toolbar class="mb-1 border-none shadow-1">
      <template #start>
        <Button
          :label="languageConfig.addTitle"
          icon="pi pi-plus"
          class="mr-2"
          @click="openNew"
          outlined
        />
      </template>
    </Toolbar>

    <div class="border-round-lg mb-4 overflow-hidden shadow-1">
      <Tabs :value="0" scrollable>
        <TabList>
          <Tab
            v-for="(tab, index) in privilegeLevels"
            :key="tab.label"
            :value="index"
          >
            <Badge :value="index + 1"></Badge>
            {{ tab.label }}
          </Tab>
        </TabList>
        <TabPanels>
          <TabPanel
            v-for="(tab, index) in privilegeLevels"
            :key="tab.sale"
            :value="index"
          >
            <div class="py-2 md:p-2">
              <p class="m-0">Скидка на все товары: {{ tab.saleAll }}</p>
              <p class="m-0">Порог входа: {{ tab.starts_from }}</p>
            </div>

            <div class="flex mt-3 gap-2">
              <Button
                :label="languageConfig.editTitle"
                @click="editPrivilege(tab)"
                outlined
                icon="pi pi-pencil"
                severity="secondary"
                size="small"
              />
              <Button
                :label="languageConfig.deleteTitle"
                @click="$emit('confirmDeletePrivilege', ['percent', tab])"
                outlined
                icon="pi pi-trash"
                severity="danger"
                size="small"
              />
            </div>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </div>

    <div class="px-1 pb-3 md:px-3">
      <h3 class="text-2xl mb-2 font-medium">Настройки</h3>

      <div class="md:px-2">
        <div
          class="flex flex-wrap align-items-center justify-content-between mb-2"
        >
          <label
            for="percent_checked"
            class="settings__title font-normal md:text-lg"
            >Включить программу</label
          >
          <ToggleSwitch
            inputId="percent_checked"
            class="switch"
            v-model="editableSettings.active"
          />
        </div>

        <div
          class="flex flex-wrap align-items-center justify-content-between mb-2"
        >
          <label
            for="percent_levels"
            class="settings__title font-normal md:text-lg"
            >Уровни привилегий</label
          >
          <InputNumber
            v-model="editableSettings.levels"
            inputId="percent_levels"
            mode="decimal"
            showButtons
            :min="0"
            :max="20"
            :step="1"
          />
        </div>

        <div class="flex justify-content-end align-items-center gap-2 mt-4">
          <Button
            :label="languageConfig.saveTitle"
            severity="success"
            @click="saveSettings"
            :disabled="isModified"
            :outlined="isModified"
          />
          <Button
            :label="languageConfig.cancel"
            severity="danger"
            @click="cancelSettingsChanges"
            :disabled="isModified"
            :outlined="isModified"
          />
        </div>
      </div>
    </div>

    <Dialog
      v-model:visible="productDialog"
      :header="productDialogText"
      :modal="true"
    >
      <div class="flex flex-col gap-6">
        <div class="col-span-6 max-w-14rem">
          <label for="label" class="block font-bold mb-3">Название</label>
          <InputText
            inputId="label"
            v-model.trim="product.label"
            :required="true"
            autofocus
            :invalid="submitted && !product.label"
            fluid
          />
          <small v-if="submitted && !product.label" class="text-red-500"
            >Это обязательное поле.</small
          >
        </div>
        <div class="col-span-6">
          <label for="saleAll" class="block font-bold mb-3"
            >Cкидка на все товары</label
          >
          <InputNumber
            v-model="product.saleAll"
            inputId="saleAll"
            mode="decimal"
            suffix="%"
            placeholder="%"
            showButtons
            :min="0"
            :max="100"
            fluid
          />
        </div>
        <div class="col-span-6">
          <label for="startsFrom" class="block font-bold mb-3"
            >Порог входа</label
          >
          <InputNumber
            v-model="product.starts_from"
            inputId="startsFrom"
            mode="decimal"
            showButtons
            :min="0"
            :max="10000"
            fluid
          />
        </div>
      </div>

      <template #footer>
        <Button
          :label="languageConfig.cancelTitle"
          icon="pi pi-times"
          text
          @click="hideDialog"
        />
        <Button
          :label="productDialogText"
          icon="pi pi-check"
          @click="saveProduct"
        />
      </template>
    </Dialog>
  </div>
</template>
