<script setup>
import { ref, readonly } from "vue";
import { settings, deepEqual, updateSettings, getSettings } from "@/settings";

import ToggleSwitch from "primevue/toggleswitch";
import InputNumber from "primevue/inputnumber";
import Button from "primevue/button";

const obj = getSettings();
const currentPersent = ref(obj.percent);
</script>

<template>
  <div class="">
    <div class="flex flex-wrap align-items-center justify-content-between mb-2">
      <label
        for="percent_checked"
        class="settings__title font-normal md:text-lg"
        >Включить программу</label
      >
      <ToggleSwitch inputId="percent_checked" v-model="currentPersent.active" />
      <ToggleSwitch
        inputId="percent_checked"
        v-model="settings.percent.active"
      />
    </div>

    <div class="flex flex-wrap align-items-center justify-content-between mb-2">
      <label for="percent_levels" class="settings__title font-normal md:text-lg"
        >Уровни привилегий</label
      >
      <InputNumber
        v-model="currentPersent.levels"
        inputId="percent_levels"
        mode="decimal"
        class=""
        showButtons
        :min="0"
        :max="20"
      />
      <InputNumber
        v-model="settings.percent.levels"
        inputId="percent_levels"
        mode="decimal"
        class=""
        showButtons
        :min="0"
        :max="20"
      />
    </div>

    <div class="flex justify-content-end align-items-center gap-2 mt-4">
      <Button
        label="Сохранить"
        severity="success"
        @click="updateSettings('percent', currentPersent)"
      />
      <Button
        label="Отменить"
        severity="danger"
        @click="currentPersent = getSettings('percent')"
      />
    </div>
  </div>
</template>
