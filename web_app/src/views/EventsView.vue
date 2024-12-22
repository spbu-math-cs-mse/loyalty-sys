<script setup>
import { ref, onMounted } from "vue";
import { useToast } from "primevue/usetoast";
import { usePrimeVue } from "primevue/config";
import { useDateFormater } from "@/stores/dateFormater";

import Panel from "primevue/panel";
import InputText from "primevue/inputtext";
import InputNumber from "primevue/inputnumber";
import FloatLabel from "primevue/floatlabel";
import Textarea from "primevue/textarea";
import DatePicker from "primevue/datepicker";
import Select from "primevue/select";
import Button from "primevue/button";
import axios from "axios";

import SectionHeaderInfo from "../components/SectionHeaderInfo.vue";

const toast = useToast();
const primevue = usePrimeVue();
const dateFormater = useDateFormater();

const languageConfig = primevue.config.locale;
const toastConfig = languageConfig.toast;

const event = ref({});
const submitted = ref(false);
const errors = ref(false);
const categotyList = ref([]);

const formSubmit = () => {
  if (
    !!event?.value.category &&
    event?.value.title?.trim() &&
    event?.value.description?.trim() &&
    event?.value.range &&
    event?.value.sale
  ) {
    submitted.value = true;
    if (event?.value.range[1] === null) {
      event.value.range[1] = event.value.range[0];
    }
    event.value.range = event.value.range.map((date) =>
      dateFormater.toYYYYMMDD(date)
    );

    axios
      .post("http://84.201.143.213:5000/event", event.value)
      .then(() => {
        toast.add({
          severity: toastConfig.severity.success,
          summary: toastConfig.summary.successTitle,
          detail: toastConfig.detail.event.add,
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
        event.value = {};
      });
  } else {
    errors.value = true;
  }
};

onMounted(() => {
  axios
    .get("http://84.201.143.213:5000/data/categories")
    .then((response) => {
      categotyList.value = response.data;
    })
    .catch((error) => {
      console.log(error);
    });
});
</script>

<template>
  <div class="events lg:py-4 py-1 md:pl-3 pl-0">
    <SectionHeaderInfo title="События" />

    <Panel :header="languageConfig.addTitle" toggleable>
      <div class="py-2 px-1 lg:px-3 flex flex-column gap-3">
        <div class="">
          <FloatLabel variant="on">
            <label for="title">Название</label>
            <InputText
              id="title"
              required="true"
              v-model.trim="event.title"
              :invalid="errors && !event.title"
              fluid
            />
          </FloatLabel>
          <small v-show="errors && !event.title" class="text-red-500"
            >Это обязательное поле.</small
          >
        </div>

        <div class="">
          <FloatLabel variant="on">
            <label for="description" class="block">Описание</label>
            <Textarea
              id="description"
              name="description"
              v-model="event.description"
              :invalid="errors && !event.description"
              fluid
              autoResize
              style="min-height: 100px"
            />
          </FloatLabel>
          <small v-show="errors && !event.description" class="text-red-500"
            >Это обязательное поле.</small
          >
        </div>

        <div>
          <FloatLabel variant="on">
            <DatePicker
              v-model="event.range"
              dateFormat="dd.mm.yy"
              selectionMode="range"
              iconDisplay="input"
              id="eventRange"
              showButtonBar
              showIcon
              :showOtherMonths="false"
              :invalid="errors && !event.range"
            />
            <label for="eventRange">Длительность</label>
          </FloatLabel>
          <small v-show="errors && !event.range" class="text-red-500"
            >Это обязательное поле.</small
          >
        </div>

        <div class="flex flex-wrap gap-2">
          <div class="flex flex-column">
            <FloatLabel variant="on" class="w-full">
              <Select
                id="category"
                v-model="event.category"
                :options="categotyList"
                placeholder="Категория"
                :invalid="errors && !event.category"
                optionLabel="label"
                showClear
                fluid
              />
              <label for="category">Категория</label>
            </FloatLabel>
            <small v-show="errors && !event.category" class="text-red-500"
              >Это обязательное поле.</small
            >
          </div>

          <span class="pi pi-arrow-right mt-2"></span>

          <div class="flex flex-column">
            <FloatLabel variant="on">
              <InputNumber
                v-model="event.sale"
                id="categorySale"
                mode="decimal"
                suffix="%"
                showButtons
                :invalid="errors && !event.sale"
                :min="1"
                :max="100"
              />
              <label for="categorySale">Скидка</label>
            </FloatLabel>
            <small v-show="errors && !event.sale" class="text-red-500"
              >Это обязательное поле.</small
            >
          </div>
        </div>

        <div class="flex justify-content-end mt-0">
          <Button
            :label="
              submitted ? languageConfig.pending : languageConfig.addTitle
            "
            outlined="true"
            @click="formSubmit"
          />
        </div>
      </div>
    </Panel>
  </div>
</template>

<style>
.p-inputnumber-input {
  max-width: 6.5rem;
}
</style>
