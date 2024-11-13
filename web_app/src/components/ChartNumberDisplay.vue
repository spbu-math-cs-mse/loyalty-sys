<script setup>
import { ref, watchEffect } from "vue";

const props = defineProps({
  title: {
    type: String,
    default: "Title",
    required: true,
  },
  number: {
    type: Number,
    default: 0,
    required: true,
  },
  beforeIcon: {
    type: String,
    required: false,
  },
  afterIcon: {
    type: String,
    required: false,
  },
  money: {
    type: String,
    required: false,
  },
});

const currentNumber = ref(0);
const counterSpeed = ref(10);

watchEffect(() => {
  if (currentNumber.value < props.number) {
    const increment = Math.ceil(props.number / 1000);
    const interval = setInterval(() => {
      currentNumber.value = Math.min(
        currentNumber.value + increment,
        props.number
      );

      if (currentNumber.value >= props.number) {
        currentNumber.value = props.number;
        clearInterval(interval);
      }
    }, counterSpeed);
  }
});
</script>

<template>
  <div class="card border-round-lg overflow-hidden shadow-1 select-none">
    <h6 class="card__title mb-2">{{ title }}</h6>
    <div class="flex align-items-center">
      <i
        v-if="beforeIcon"
        class="card__icon text-lg card-icon pi mr-2"
        :class="beforeIcon"
      ></i>
      <span class="card__number text-2xl font-medium"
        ><span>{{ money ? money : "" }}</span> {{ currentNumber }}</span
      >
      <i class="card__icon text-lg card-icon pi ml-3" :class="afterIcon"></i>
    </div>
  </div>
</template>

<style scoped>
.card {
  padding: 10px 15px;
  padding-top: 18px;
  background: var(--p-surface-0);
  min-width: 250px;
}

.card__title {
  font-family: "Montserrat";
  font-size: 18px;
  font-weight: 600;
  color: var(--p-text-color);
}

.card__number {
  font-family: "Montserrat";
  color: var(--p-text-color);
  transition: 0.2s ease;
}

.card__icon.pi-arrow-up-right {
  color: var(--p-green-500);
}
.card__icon.pi-arrow-down-right {
  color: var(--p-red-500);
}
.card__icon.pi-users {
  color: var(--p-blue-500);
}
</style>
