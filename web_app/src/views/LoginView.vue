<script setup>
import { ref } from "vue";
import { Form } from "@primevue/forms";
import { useToast } from "primevue/usetoast";
import { usePrimeVue } from "primevue/config";
import { useUserStore } from "@/stores/user";

import InputText from "primevue/inputtext";
import Password from "primevue/password";
import Button from "primevue/button";
import axios from "axios";
import router from "@/router";

const user = useUserStore();
const toast = useToast();
const primevue = usePrimeVue();

const languageConfig = primevue.config.locale;
const toastConfig = languageConfig.toast;

const formData = ref({
  username: "",
  password: "",
});
const waitingData = ref(false);
const errorTypes = {
  nullLogin: "NULL_LOGIN",
  nullPassword: "NULL_PASSWORD",
  invalidLogin: "INVALID_LOGIN",
  invalidPassword: "INVALID_PASSWORD",
};

const onFormSubmit = () => {
  if (formData.value.username.trim() === "") {
    toast.add({
      severity: toastConfig.severity.error,
      summary: toastConfig.summary.error,
      detail: toastConfig.forms.nullLogin,
      life: 3000,
    });
    return;
  }

  if (formData.value.password.trim() === "") {
    toast.add({
      severity: toastConfig.severity.error,
      summary: toastConfig.summary.error,
      detail: toastConfig.forms.nullPassword,
      life: 3000,
    });
    return;
  }

  waitingData.value = true;
  const sendingData = {
    login: formData.value.username,
    password: formData.value.password,
  };

  sendingData.password = user.getHash(sendingData.password);
  axios
    .post("http://84.201.143.213:5000/login", sendingData)
    .then((response) => {
      if (response.data.auth) {
        localStorage.setItem("auth", JSON.stringify(response.data.auth));
        user.auth = response.data.auth;
      } else if (response.data.error !== undefined) {
        switch (response.data.error) {
          case errorTypes.invalidPassword:
            formData.value.password = "";
            toast.add({
              severity: toastConfig.severity.error,
              summary: toastConfig.summary.error,
              detail: toastConfig.forms.invalidPassword,
              life: 3000,
            });
            break;

          case errorTypes.invalidLogin:
            formData.value.username = "";
            formData.value.password = "";
            toast.add({
              severity: toastConfig.severity.error,
              summary: toastConfig.summary.error,
              detail: toastConfig.forms.incorrectLogin,
              life: 3000,
            });
            break;

          default:
            toast.add({
              severity: toastConfig.severity.error,
              summary: toastConfig.summary.error,
              detail: response.data.error,
              life: 3000,
            });
        }
      }
    })
    .catch((error) => {
      console.log(error);
    })
    .finally(() => {
      waitingData.value = false;
      router.push("/");
    });
};
</script>

<template>
  <div class="flex align-items-center h-screen justify-content-center">
    <Form @submit="onFormSubmit" class="flex flex-column">
      <h4 class="font-normal text-xl mb-3">{{ toastConfig.forms.login }}</h4>
      <div class="flex flex-column gap-2">
        <InputText
          name="username"
          v-model="formData.username"
          type="text"
          :placeholder="toastConfig.forms.loginTitle"
        />
        <Password
          name="password"
          v-model="formData.password"
          :placeholder="toastConfig.forms.password"
          :feedback="false"
          toggleMask
        />
        <Button
          type="submit"
          severity="secondary"
          :label="
            waitingData ? languageConfig.pending : toastConfig.forms.login
          "
          :disabled="waitingData"
        />
      </div>
    </Form>
  </div>
</template>
