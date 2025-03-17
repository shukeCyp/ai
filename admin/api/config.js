// 默认API基础URL
let baseURL = 'http://aiapi.lyvideo.top';
// let baseURL = 'http://localhost:8801';


// 设置基础URL的方法
export const setBaseURL = (url) => {
    baseURL = url;
};
  
// 获取基础URL的方法
export const getBaseURL = () => {
    return baseURL;
};

// 获取存储的token
export const getToken = () => {
    return localStorage.getItem('token') || '';
};

// 设置token
export const setToken = (token) => {
    localStorage.setItem('token', token);
};

// 移除token
export const removeToken = () => {
    localStorage.removeItem('token');
};

// 统一请求方法
export const request = (options) => {
  return new Promise((resolve, reject) => {
    // 获取token并添加到请求头
    const token = getToken();
    const header = {
      ...(options.header || {})
    };
    
    if (token) {
      header['Authorization'] = `Bearer ${token}`;
    }
    
    // 处理URL和查询参数
    let url = `${baseURL}${options.url}`;
    
    // 使用fetch API
    fetch(url, {
      method: options.method || 'GET',
      headers: header,
      body: options.data ? JSON.stringify(options.data) : undefined
    })
    .then(response => {
      // 检查是否是401错误（未授权）
      if (response.status === 401) {
        // 清除token
        removeToken();
        
        // 重定向到登录页面
        const currentPath = window.location.pathname;
        window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`;
        
        throw new Error('登录已过期，请重新登录');
      }
      
      if (response.ok) {
        return response.json();
      } else {
        return response.json().then(errorData => {
          throw new Error(errorData.detail ? JSON.stringify(errorData.detail) : `请求失败：${response.status}`);
        });
      }
    })
    .then(data => {
      resolve(data);
    })
    .catch(err => {
      reject(err);
    });
  });
};