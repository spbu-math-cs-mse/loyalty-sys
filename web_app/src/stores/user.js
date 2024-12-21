import { defineStore } from "pinia";
const CryptoJS = require("crypto-js");

export const useUserStore = defineStore("user", {
  state: () => ({
    auth: !!JSON.parse(localStorage.getItem("auth")),
  }),
  actions: {
    async getHash(string) {
      return CryptoJS.SHA512(string).toString(CryptoJS.enc.Hex);
    },
  },
});
