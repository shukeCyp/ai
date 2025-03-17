import { createApp } from 'vue';
import Toast from '../components/Toast.vue';

const toast = {
  install(app) {
    // 创建一个挂载点
    const mountPoint = document.createElement('div');
    document.body.appendChild(mountPoint);
    
    // 创建 Toast 实例
    const toastApp = createApp(Toast);
    const toastInstance = toastApp.mount(mountPoint);
    
    // 添加到全局属性
    app.config.globalProperties.$toast = {
      show: (message, type, duration) => toastInstance.show(message, type, duration),
      success: (message, duration) => toastInstance.success(message, duration),
      error: (message, duration) => toastInstance.error(message, duration),
      warning: (message, duration) => toastInstance.warning(message, duration),
      info: (message, duration) => toastInstance.info(message, duration)
    };
    
    // 也可以通过 inject 在组件中使用
    app.provide('toast', app.config.globalProperties.$toast);
  }
};

export default toast; 