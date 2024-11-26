<script setup>
defineProps({
  title: {
    type: String,
    default: "Title",
  },
  subtitle: {
    type: String,
  },
});
</script>

<template>
  <div class="mb-5 pl-1 md:pl-0">
    <h3 class="text-3xl mb-2 font-medium">{{ title }}</h3>
    <p class="text-md mb-2 font-normal">{{ subtitle }}</p>
  </div>
</template>

<style scoped>
p {
  text-indent: 2px;
}
</style>
