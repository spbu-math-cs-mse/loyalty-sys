<script setup>
import Tabs from "primevue/tabs";
import TabList from "primevue/tablist";
import Tab from "primevue/tab";
import TabPanels from "primevue/tabpanels";
import TabPanel from "primevue/tabpanel";
import Toolbar from "primevue/toolbar";
import Badge from "primevue/badge";
import Dialog from "primevue/dialog";
import InputNumber from "primevue/inputnumber";
import InputText from "primevue/inputtext";
import Button from "primevue/button";

import SectionHeaderInfo from "../components/SectionHeaderInfo.vue";

import { ref } from "vue";
import { useToast } from "primevue/usetoast";
import { usePrimeVue } from "primevue/config";

const toast = useToast();
const primevue = usePrimeVue();
const languageConfig = primevue.config.locale;
const toastConfig = languageConfig.toast;

const product = ref({});
const productDialog = ref(false);
const submitted = ref(false);
const productDialogText = ref();
const deleteProductDialog = ref(false);

const privilegeLevels = ref([
  {
    label: "Уровень 1",
    sale: {
      all: 5,
    },
    starts_from: 0,
  },
  {
    label: "Уровень 2",
    sale: {
      all: 15,
    },
    starts_from: 2000,
  },
  {
    label: "Уровень 3",
    sale: {
      all: 25,
    },
    starts_from: 5000,
  },
]);

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
const confirmDeleteProduct = (prod) => {
  product.value = prod;
  deleteProductDialog.value = true;
};
const deleteProduct = () => {
  privilegeLevels.value = privilegeLevels.value.filter(
    (val) => val.label !== product.value.label
  );
  deleteProductDialog.value = false;
  product.value = {};
  toast.add({
    severity: toastConfig.severity.success,
    summary: toastConfig.summary.success,
    detail: toastConfig.detail.privillege.delete,
    life: 3000,
  });
};
const editProduct = (prod) => {
  productDialogText.value = languageConfig.editTitle;
  product.value = { ...prod };
  productDialog.value = true;
};
const findIndexByLabel = (label) => {
  let index = -1;
  for (let i = 0; i < privilegeLevels.value.length; i++) {
    if (privilegeLevels.value[i].label === label) {
      index = i;
      break;
    }
  }

  return index;
};
const saveProduct = () => {
  submitted.value = true;

  if (product?.value.label?.trim()) {
    if (product.value.label) {
      console.log(
        "=====================     1     ==========================="
      );
      privilegeLevels.value[findIndexByLabel(product.value.label)] =
        product.value;
      toast.add({
        severity: toastConfig.severity.success,
        summary: toastConfig.summary.successTitle,
        detail: toastConfig.detail.privillege.edit,
        life: 3000,
      });
    } else {
      console.log("=====================    2     ===========================");
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
</script>

<template>
  <div class="privilege container__wrapper lg:py-4 py-1 md:pl-3 pl-0">
    <SectionHeaderInfo title="Привилегии" />

    <Toolbar class="mb-4">
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

    <div class="border-round-lg overflow-hidden shadow-1">
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
            <div class="p-2">
              <p class="m-0">Скидка на все товары: {{ tab.sale.all }}</p>
              <p class="m-0">Порог входа: {{ tab.starts_from }}</p>
            </div>

            <div class="flex mt-3 gap-2">
              <Button
                :label="languageConfig.editTitle"
                @click="editProduct(tab)"
                outlined
                icon="pi pi-pencil"
                severity="secondary"
                size="small"
              />
              <Button
                :label="languageConfig.deleteTitle"
                @click="confirmDeleteProduct(tab)"
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
          @click="deleteProduct"
        />
      </template>
    </Dialog>

    <Dialog
      v-model:visible="productDialog"
      :header="productDialogText"
      :modal="true"
    >
      <div class="flex flex-col gap-6">
        <div class="col-span-6 max-w-14rem">
          <label for="label" class="block font-bold mb-3">Название</label>
          <InputText
            id="label"
            v-model.trim="product.label"
            required="true"
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
