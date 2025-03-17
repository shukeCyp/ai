# 构建阶段
FROM node:20
WORKDIR /app

# 使用淘宝 NPM 镜像
RUN npm config set registry https://registry.npmmirror.com

COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 安装简单的 HTTP 服务器来提供静态内容
RUN npm install -g serve

EXPOSE 80
CMD ["serve", "-s", "dist", "-l", "80"] 