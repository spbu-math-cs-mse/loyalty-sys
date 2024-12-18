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
const toastConfig = languageConfig.toast.forms;

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
      severity: "error",
      summary: "Ошибка",
      detail: toastConfig.nullLogin,
      life: 3000,
    });
    return;
  }

  if (formData.value.password.trim() === "") {
    toast.add({
      severity: "error",
      summary: "Ошибка",
      detail: toastConfig.nullPassword,
      life: 3000,
    });
    return;
  }

  waitingData.value = true;
  const sendingData = {
    username: formData.value.username,
    password: formData.value.password,
  };
  user
    .getHash(sendingData.password)
    .then((hex) => (sendingData.password = hex))
    .then(() => {
      axios
        .post("http://84.201.143.213:5000/login", sendingData)
        .then((response) => {
          console.log(response);

          if (response.error !== "") {
            switch (response.error) {
              case errorTypes.invalidPassword:
                formData.value.password = "";
                toast.add({
                  severity: "error",
                  summary: "Ошибка",
                  detail: response.error.type,
                  life: 3000,
                });
                break;

              case errorTypes.invalidLogin:
                formData.value.username = "";
                formData.value.password = "";
                toast.add({
                  severity: "error",
                  summary: "Ошибка",
                  detail: response.error.type,
                  life: 3000,
                });
                break;

              default:
                toast.add({
                  severity: "error",
                  summary: "Ошибка",
                  detail: response.error.type,
                  life: 3000,
                });
            }
            return;
          }

          if (response.auth) {
            localStorage.setItem("auth", JSON.stringify(response.auth));
            user.auth = response.auth;
          }
        })
        .catch((error) => {
          console.log(error);
        })
        .finally(() => {
          /* Remove to then method after
          adding data of admins to database */
          waitingData.value = false;
          localStorage.setItem("auth", true);
          user.auth = true;
          router.push("/");
        });

      toast.add({
        severity: "success",
        summary: "Форма отправлена",
        life: 3000,
      });
    });
};
</script>

<template>
  <div class="flex align-items-center h-screen justify-content-center">
    <Form @submit="onFormSubmit" class="flex flex-column">
      <h4 class="font-normal text-xl mb-3">{{ toastConfig.login }}</h4>
      <div class="flex flex-column gap-2">
        <InputText
          name="username"
          v-model="formData.username"
          type="text"
          :placeholder="toastConfig.loginTitle"
        />
        <Password
          name="password"
          v-model="formData.password"
          :placeholder="toastConfig.password"
          :feedback="false"
          toggleMask
        />
        <Button
          type="submit"
          severity="secondary"
          :label="toastConfig.login"
          :disabled="waitingData"
        />
      </div>
    </Form>
  </div>
</template>
