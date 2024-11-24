<script setup>
import { ref } from "vue";

import ToggleSwitch from "primevue/toggleswitch";
import InputNumber from "primevue/inputnumber";

const checked = ref(false);
const levels = ref(0);

</script>

<template>
  <div class="">
    <div class="flex flex-wrap align-content-center justify-content-between mb-2">
        <label for="percent_checked" class="settings__title font-normal text-lg">Включить программу</label>
        <ToggleSwitch inputId="percent_checked" v-model="checked" />
    </div>
    
    <div class="flex flex-wrap align-content-center justify-content-between mb-2">
        <label for="percent_levels" class="settings__title font-normal text-lg">Уровни привилегий</label>
        <InputNumber
          v-model="levels"
          inputId="percent_levels"
          mode="decimal"
          class=""
          showButtons
          :min="0"
          :max="20"
        />
    </div>
  </div>

</template>