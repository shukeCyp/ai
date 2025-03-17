import { get, post, del } from './config.js';

// 生成视频
export function generateVideo(formData) {
  return post('/generate_video/generate_video', formData, null, null, true);
}

// 获取视频生成任务状态
export function getVideoTaskStatus(taskId) {
  return get(`/generate_video/task_status/${taskId}`);
}

// 获取视频生成历史记录
export function getVideoHistory() {
  return get('/generate_video/history');
}

// 获取用户视频记录
export function getUserVideos(page = 1, pageSize = 10) {
  console.log(`调用 getUserVideos API: page=${page}, pageSize=${pageSize}`);
  return get('/user/video/videos', { page, page_size: pageSize });
}

// 删除用户视频记录
export function deleteUserVideo(videoId) {
  return del(`/user/video/videos/${videoId}`);
}