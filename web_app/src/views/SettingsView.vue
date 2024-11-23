<script setup>
import { ref } from "vue";
import { useToast } from "primevue/usetoast";
import { usePrimeVue } from "primevue/config";

import Tabs from 'primevue/tabs';
import TabList from 'primevue/tablist';
import Tab from 'primevue/tab';
import TabPanels from 'primevue/tabpanels';
import TabPanel from 'primevue/tabpanel';
import Toolbar from "primevue/toolbar";
import Badge from 'primevue/badge';
import Dialog from "primevue/dialog";
import InputNumber from "primevue/inputnumber";
import InputText from "primevue/inputtext";
import Button from "primevue/button";

import SectionHeaderInfo from "../components/SectionHeaderInfo.vue";
import PercentView from './PercentView.vue';
import PointView from './PointView.vue';


const toolbarSettings = ref([
  {
    label: 'Процентная',
    component: PercentView,
  },
  {
    label: 'Бальная',
    component: PointView,
  },
]);

const value = ref(0);
const toast = useToast();
const primevue = usePrimeVue();
const languageConfig = primevue.config.locale;
const toastConfig = languageConfig.toast

</script>

<template>
  <div class="privilege lg:py-4 py-1 md:pl-3 pl-0">
    <SectionHeaderInfo title="Настройки" />

    <Toolbar>
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

    <div class="p-3">
      <component :is="toolbarSettings[value].component" />
    </div>

  </div>
</template>
