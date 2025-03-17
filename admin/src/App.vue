<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App',
  methods: {
    // 添加登录方法
    login(username, password) {
      const url = `http://localhost:8801/admin/user/login?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`;
      
      return fetch(url, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('登录失败');
        }
        return response.json();
      })
      .then(data => {
        console.log('登录成功:', data);
        return data;
      })
      .catch(error => {
        console.error('登录错误:', error);
        throw error;
      });
    }
  }
}
</script>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  width: 100%;
  height: 100vh;
}
</style>
