<template>
  <div class="login-container">
    <el-form ref="loginForm" :model="loginForm" :rules="loginRules" class="login-form" autocomplete="on" label-position="left">
      <div class="title-container">
        <h3 class="title">管理系统登录</h3>
      </div>

      <el-form-item prop="username">
        <el-input
          ref="username"
          v-model="loginForm.username"
          placeholder="用户名"
          name="username"
          type="text"
          tabindex="1"
          autocomplete="on"
          prefix-icon="el-icon-user"
        />
      </el-form-item>

      <el-form-item prop="password">
        <el-input
          ref="password"
          v-model="loginForm.password"
          placeholder="密码"
          name="password"
          :type="passwordVisible ? 'text' : 'password'"
          tabindex="2"
          autocomplete="on"
          prefix-icon="el-icon-lock"
          :suffix-icon="passwordVisible ? 'el-icon-view' : 'el-icon-hide'"
          @suffix-icon-click="passwordVisible = !passwordVisible"
        />
      </el-form-item>

      <el-button :loading="loading" type="primary" style="width:100%;margin-bottom:30px;" @click="handleLogin">登录</el-button>
    </el-form>
  </div>
</template>

<script>
import { login } from '../../api/login.js';
import { setToken } from '../../api/config.js';

export default {
  name: 'LoginPage',
  data() {
    const validateUsername = (rule, value, callback) => {
      if (!value) {
        callback(new Error('请输入用户名'))
      } else {
        callback()
      }
    }
    const validatePassword = (rule, value, callback) => {
      if (value.length < 6) {
        callback(new Error('密码不能少于6位'))
      } else {
        callback()
      }
    }
    return {
      loginForm: {
        username: 'admin',
        password: '123456'
      },
      loginRules: {
        username: [{ required: true, trigger: 'blur', validator: validateUsername }],
        password: [{ required: true, trigger: 'blur', validator: validatePassword }]
      },
      passwordVisible: false,
      loading: false,
      redirect: undefined
    }
  },
  watch: {
    $route: {
      handler: function(route) {
        this.redirect = route.query && route.query.redirect
      },
      immediate: true
    }
  },
  methods: {
    handleLogin() {
      this.$refs.loginForm.validate(valid => {
        if (valid) {
          this.loading = true
          
          // 调用登录接口
          login(this.loginForm.username, this.loginForm.password)
            .then(response => {
              // 假设响应中包含token
              const token = response.data?.token || response.token || 'admin-token';
              
              // 存储token
              setToken(token);
              
              // 显示登录成功消息
              this.$message({
                message: '登录成功',
                type: 'success'
              });
              
              // 跳转到首页或者重定向页面
              this.$router.push({ path: this.redirect || '/' });
            })
            .catch(error => {
              console.error('登录失败:', error);
              this.$message.error(error.message || '登录失败，请检查用户名和密码');
            })
            .finally(() => {
              this.loading = false;
            });
        } else {
          console.log('表单验证失败');
          return false;
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.login-container {
  min-height: 100%;
  width: 100%;
  background-color: #2d3a4b;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-form {
  position: relative;
  width: 520px;
  max-width: 100%;
  padding: 160px 35px 0;
  margin: 0 auto;
  overflow: hidden;
}

.title-container {
  position: relative;
  margin-bottom: 30px;
}

.title {
  font-size: 26px;
  color: #eee;
  margin: 0 auto 40px auto;
  text-align: center;
  font-weight: bold;
}
</style> 