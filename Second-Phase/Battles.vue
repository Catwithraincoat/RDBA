<template>
    <div class="home-link">
        <router-link to="/main"><i class="ri-arrow-left-line"></i></router-link>
    </div>
    <div class="container">
        <header>
            <h1>BATTLES</h1>
        </header>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>NO</th>
                        <th>Time</th>
                        <th>Planet</th>
                        <th>Enemy</th>
                        <th>Deccription</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>12345</td>
                        <td>1963-Present</td>
                        <td>Galifrey</td>
                        <td>Doctor</td>
                        <td>Someone died</td>
                    </tr>
                    <tr>
                        <td>12345</td>
                        <td>1963-Present</td>
                        <td>Galifrey</td>
                        <td>Doctor</td>
                        <td>Someone died</td>
                    </tr>
                    <tr>
                        <td>12345</td>
                        <td>1963-Present</td>
                        <td>Galifrey</td>
                        <td>Doctor</td>
                        <td>Someone died</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const battles = ref([]);

onMounted(async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get('http://localhost:5001/battles', {
      headers: { Authorization: `Bearer ${token}` }
    });
    battles.value = response.data;
  } catch (err) {
    console.error('Failed to load battles');
  }
});
</script>

<style lang="scss" scoped>
h1 {
    font-size: 8em;
    text-align: center;
}
</style> 
