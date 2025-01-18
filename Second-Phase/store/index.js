import { reactive } from 'vue';

export const store = reactive({
  user: null,
  token: null,
  
  setUser(userData) {
    this.user = userData;
  },
  
  setToken(token) {
    this.token = token;
    localStorage.setItem('token', token);
  },
  
  logout() {
    this.user = null;
    this.token = null;
    localStorage.removeItem('token');
  }
}); 
