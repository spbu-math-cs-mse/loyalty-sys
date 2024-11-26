import { reactive } from "vue";

const settings = reactive({
  point: {
    active: false,
    levels: 5,
  },
  percent: {
    active: false,
    levels: 10,
  },
});

function deepEqual(first, second) {
  if (first === second) return true;

  if (
    typeof first !== "object" ||
    first === null ||
    typeof second !== "object" ||
    second === null
  ) {
    return false;
  }

  const keysFirst = Object.keys(first);
  const keysSecond = Object.keys(second);

  if (keysFirst.length !== keysSecond.length) return false;

  return keysFirst.every((key) => {
    return keysSecond.includes(key) && deepEqual(first[key], second[key]);
  });
}

function updateSettings(key, newSettings) {
  settings.value[key] = newSettings;
}

function getSettings(key) {
  return key ? settings.value[key] : settings.value;
}

export { deepEqual, updateSettings, getSettings };
