<script setup>
import { ref } from "vue";
import { useToast } from "primevue/usetoast";
import { usePrimeVue } from "primevue/config";
import { useUserStore } from "@/stores/user";

import Toolbar from "primevue/toolbar";
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import Password from "primevue/password";
import Dialog from "primevue/dialog";
import axios from "axios";

import SectionHeaderInfo from "../components/SectionHeaderInfo.vue";

const user = useUserStore();
const toast = useToast();
const primevue = usePrimeVue();

const languageConfig = primevue.config.locale;
const toastConfig = languageConfig.toast;

const product = ref({});
const productDialogText = ref();
const submitted = ref(false);
const errors = ref(false);
const productDialog = ref(false);

const openNew = () => {
  productDialogText.value = languageConfig.addTitle;
  product.value = {
    login: "",
    password: "",
  };
  submitted.value = false;
  productDialog.value = true;
};

const hideDialog = () => {
  productDialog.value = false;
  submitted.value = false;
};

const formSubmit = () => {
  if (product?.value.login?.trim() && product?.value.password?.trim()) {
    submitted.value = true;
    axios
      .post("http://84.201.143.213:5000/register_admin", {
        login: product.value.login,
        password: user.getHash(product.value.password),
      })
      .then(() => {
        toast.add({
          severity: toastConfig.severity.success,
          summary: toastConfig.summary.successTitle,
          detail: toastConfig.severity.admin.add,
          life: 3000,
        });
      })
      .catch((e) => {
        console.log(e);
        toast.add({
          severity: toastConfig.severity.error,
          summary: toastConfig.summary.error,
          detail: e.message,
          life: 3000,
        });
      })
      .finally(() => {
        submitted.value = false;
        errors.value = false;
        product.value = {};
        hideDialog();
      });
  } else {
    errors.value = true;
  }
};
</script>

<template>
  <div class="admins lg:py-4 py-1 md:pl-3 pl-0">
    <SectionHeaderInfo title="Админы" />

    <div class="w-full">
      <Toolbar class="mb-6">
        <template #start>
          <Button
            :label="languageConfig.addTitle"
            outlined
            icon="pi pi-plus"
            class="mr-2"
            @click="openNew"
          />
        </template>
      </Toolbar>
    </div>

    <Dialog
      v-model:visible="productDialog"
      :header="productDialogText"
      :modal="true"
    >
      <div class="flex gap-6">
        <div class="col-span-6 max-w-14rem">
          <label for="login" class="block font-bold mb-3">Логин</label>
          <InputText
            id="login"
            required="true"
            v-model.trim="product.login"
            :invalid="errors && !product.login"
            autofocus
            fluid
          />
          <small v-show="errors && !product.login" class="text-red-500"
            >Это обязательное поле.</small
          >
        </div>
        <div class="col-span-6">
          <label for="password" class="block font-bold mb-3">Пароль</label>
          <Password
            id="password"
            name="password"
            v-model="product.password"
            :invalid="errors && !product.password"
            :placeholder="toastConfig.password"
            :feedback="false"
            toggleMask
            fluid
          />
          <small v-show="errors && !product.password" class="text-red-500"
            >Это обязательное поле.</small
          >
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
          :label="submitted ? languageConfig.pending : productDialogText"
          :disabled="submitted"
          icon="pi pi-check"
          @click="formSubmit"
        />
      </template>
    </Dialog>
  </div>
</template>
