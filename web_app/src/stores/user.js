import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    auth: !!JSON.parse(localStorage.getItem('auth')),
  }),
  actions: {
    async getHash(string) {
      const utf8 = new TextEncoder().encode(string);
      const hashBuffer = await crypto.subtle.digest('SHA-512', utf8);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const hashHex = hashArray
        .map((bytes) => bytes.toString(16).padStart(2, '0'))
        .join('');
      return hashHex;
    }
  },
})
