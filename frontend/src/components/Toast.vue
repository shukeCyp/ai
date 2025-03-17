<template>
  <div class="toast-container">
    <transition-group name="toast">
      <div 
        v-for="toast in toasts" 
        :key="toast.id" 
        class="toast"
        :class="[toast.type]"
      >
        <div class="toast-content">
          <i :class="getIconClass(toast.type)" class="mr-2"></i>
          <span>{{ toast.message }}</span>
        </div>
      </div>
    </transition-group>
  </div>
</template>

<script>
export default {
  name: 'Toast',
  data() {
    return {
      toasts: [],
      nextId: 0
    }
  },
  methods: {
    getIconClass(type) {
      switch(type) {
        case 'success': return 'fas fa-check-circle';
        case 'error': return 'fas fa-exclamation-circle';
        case 'warning': return 'fas fa-exclamation-triangle';
        default: return 'fas fa-info-circle';
      }
    },
    show(message, type = 'info', duration = 3000) {
      const id = this.nextId++;
      this.toasts.push({ id, message, type });
      
      setTimeout(() => {
        this.toasts = this.toasts.filter(toast => toast.id !== id);
      }, duration);
    },
    success(message, duration) {
      this.show(message, 'success', duration);
    },
    error(message, duration) {
      this.show(message, 'error', duration);
    },
    warning(message, duration) {
      this.show(message, 'warning', duration);
    },
    info(message, duration) {
      this.show(message, 'info', duration);
    }
  }
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 15%;
  left: 50%;
  transform: translate(-50%, 0);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.toast {
  margin-bottom: 10px;
  padding: 16px 24px;
  border-radius: 8px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  min-width: 300px;
  max-width: 400px;
  background-color: white;
  transition: all 0.3s ease;
  font-size: 16px;
  font-weight: 500;
}

.toast-content {
  display: flex;
  align-items: center;
  width: 100%;
  justify-content: center;
}

.toast-content i {
  font-size: 20px;
  margin-right: 12px;
}

.toast.success {
  background-color: #f0f9eb;
  border-left: 4px solid #67c23a;
  color: #67c23a;
}

.toast.error {
  background-color: #fef0f0;
  border-left: 4px solid #f56c6c;
  color: #f56c6c;
}

.toast.warning {
  background-color: #fdf6ec;
  border-left: 4px solid #e6a23c;
  color: #e6a23c;
}

.toast.info {
  background-color: #f4f4f5;
  border-left: 4px solid #909399;
  color: #909399;
}

.toast-enter-active, .toast-leave-active {
  transition: all 0.3s;
}

.toast-enter-from, .toast-leave-to {
  opacity: 0;
  transform: translateY(30px);
}
</style> 