<script setup>
import Stepper from "primevue/stepper";
import StepList from "primevue/steplist";
import StepPanels from "primevue/steppanels";
import StepItem from "primevue/stepitem";
import Step from "primevue/step";
import StepPanel from "primevue/steppanel";
import Button from "primevue/button";

import SectionHeaderInfo from "../components/SectionHeaderInfo.vue";

import { ref } from "vue";

const stepItems = ref([
  {
    label: "Уровень 1",
    icon: "pi pi-user",
    content: "Скидка 5% на кросовки",
  },
  {
    label: "Уровень 2",
    icon: "pi pi-user",
    content: "Скидка 10% на одежду и обувь",
  },
  {
    label: "Уровень 3",
    icon: "pi pi-user",
    content: "Скидка 15% на все товары",
  },
]);
</script>

<template>
  <div class="privilege lg:py-4 py-1 md:pl-3 pl-0">
    <SectionHeaderInfo title="Привилегии" />

    <div class="mt-2">
      <Stepper value="1">
        <StepItem v-for="(step, index) in stepItems" :value="`${++index}`">
          <Step>{{ step.label }}</Step>
          <StepPanel v-slot="{ activateCallback }" class="border-round-lg">
            <div class="flex flex-col">
              <div
                class="rounded bg-surface-50 py-3 flex-auto flex justify-center items-center font-medium"
              >
                {{ step.content }}
              </div>
            </div>
            <div class="py-5">
              <Button
                v-if="index > 1"
                severity="secondary"
                class="mr-2 text-sm"
                label="Back"
                @click="activateCallback(`${index - 1}`)"
              />
              <Button
                v-if="index < stepItems.length"
                class="text-sm"
                label="Next"
                @click="activateCallback(`${index + 1}`)"
              />
            </div>
          </StepPanel>
        </StepItem>
      </Stepper>
    </div>
  </div>
</template>
