import { createRouter, createWebHistory } from 'vue-router'
import Account from '../components/Account.vue'
import Battles from '../components/Battles.vue'
import Character from '../components/Character.vue'
import History from '../components/History.vue'
import Login from '../components/Login.vue'
import Main from '../components/Main.vue'
import MsgPage from '../components/Msg-page.vue'
import Msg from '../components/Msg.vue'
import Recent from '../components/Recent.vue'
import Search from '../components/Search.vue'
import Signup from '../components/Signup.vue'
import Welcome from '../components/Welcome.vue'

const routes = [
  {
    path: '/',
    name: 'Welcome',
    component: Welcome
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/signup',
    name: 'Signup',
    component: Signup
  },
  {
    path: '/main',
    name: 'Main',
    component: Main
  },
  {
    path: '/account',
    name: 'Account',
    component: Account
  },
  {
    path: '/battles',
    name: 'Battles',
    component: Battles
  },
  {
    path: '/character',
    name: 'Character',
    component: Character
  },
  {
    path: '/history',
    name: 'History',
    component: History
  },
  {
    path: '/msg-page',
    name: 'MsgPage',
    component: MsgPage
  },
  {
    path: '/msg',
    name: 'Msg',
    component: Msg
  },
  {
    path: '/recent',
    name: 'Recent',
    component: Recent
  },
  {
    path: '/search',
    name: 'Search',
    component: Search
  }
  // другие маршруты...
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 
