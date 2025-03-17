// 默认API基础URL
// let baseURL = 'http://localhost:8801';
let baseURL = 'http://aiapi.lyvideo.top';

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

// 生成随机 MAC 地址的辅助函数
function generateUUID() {
  // 生成随机的十六进制数
  const hexDigits = '0123456789abcdef';
  let uuid = '';
  
  // UUID 格式: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
  // 其中 y 是 8, 9, a, 或 b 中的一个
  for (let i = 0; i < 36; i++) {
    if (i === 8 || i === 13 || i === 18 || i === 23) {
      uuid += '-';
    } else if (i === 14) {
      uuid += '4'; // 版本 4 的 UUID
    } else if (i === 19) {
      uuid += hexDigits.charAt((Math.random() * 4) + 8); // 8, 9, a, 或 b
    } else {
      uuid += hexDigits.charAt(Math.floor(Math.random() * 16));
    }
  }
  
  // 保存到本地存储，以便下次使用
  localStorage.setItem('Mac', uuid);
  return uuid;
}

// 生成验证令牌
const generateToken = (timestamp) => {
  // 简单的基于时间戳的令牌生成
  return btoa(`secure_${timestamp}_${Math.random().toString(36).substring(2, 15)}`);
};

// 生成蜜罐请求头
const generateHoneypotHeaders = () => {
  const timestamp = Date.now();
  return {
    // 看似正常的请求头
    'X-Request-Time': timestamp,
    // 蜜罐请求头 (看起来像正常的跟踪或分析ID)
    'X-Track-ID': btoa(`${timestamp}_${Math.random()}`),
    // 验证请求头
    'X-Verify-Token': generateToken(timestamp)
  };
};

// 统一请求方法
export const request = (options) => {
  return new Promise((resolve, reject) => {
    // 获取token并添加到请求头
    const token = getToken();
    const header = {
      ...(options.isFormData ? {} : { 'Content-Type': 'application/json' }),
      ...(options.header || {}),
      ...generateHoneypotHeaders() // 添加蜜罐请求头
    };
    
    // 添加 MAC 地址到请求头
    const macAddress = localStorage.getItem('Mac') || generateUUID();
    header['Mac'] = macAddress;
    
    if (token) {
      header['Authorization'] = `Bearer ${token}`;
    }
    
    // 处理URL和查询参数
    let url = `${baseURL}${options.url}`;
    if (options.params) {
      const queryString = new URLSearchParams(options.params).toString();
      url = `${url}${url.includes('?') ? '&' : '?'}${queryString}`;
    }
    
    // 准备请求配置
    const fetchOptions = {
      method: options.method || 'GET',
      headers: header,
    };
    
    // 如果有请求体，添加到配置中
    if (options.data) {
      // 如果是 FormData，直接使用，不要 JSON.stringify
      fetchOptions.body = options.isFormData ? options.data : JSON.stringify(options.data);
    }
    
    // 使用fetch API
    fetch(url, fetchOptions)
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
      console.error('请求错误:', err);
      reject(err);
    });
  });
};

// 封装常用请求方法
export const get = (url, params, header) => {
  return request({ url, method: 'GET', params, header });
};

export const post = (url, data, header, params, isFormData = false) => {
  return request({ url, method: 'POST', data, header, params, isFormData });
};

export const put = (url, data, header) => {
  return request({ url, method: 'PUT', data, header });
};

export const del = (url, params, header) => {
  return request({ url, method: 'DELETE', params, header });
};