import { defineStore } from "pinia";

export const useDateFormater = defineStore("dateFormater", {
  state: () => ({}),
  actions: {
    toYYYYMM(date) {
      return date
        .toLocaleString("en-CA", { year: "numeric", month: "2-digit" })
        .replace("/", "-");
    },
    toYYYYMMDD(date) {
      return date
        .toLocaleString("en-CA", {
          year: "numeric",
          month: "2-digit",
          day: "2-digit",
        })
        .replace("/", "-");
    },
  },
});
