CREATE TABLE IF NOT EXISTS runway_account (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    as_team_id VARCHAR(255) NOT NULL,
    token VARCHAR(255) NOT NULL,
    plan_expires TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS runway_session (
    id INT AUTO_INCREMENT PRIMARY KEY,
    runway_id INT NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (runway_id) REFERENCES runway_account(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    mac VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS user_carmine (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    carmine VARCHAR(255) NOT NULL,
    duration INT NOT NULL COMMENT '时长（单位：天）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    activated_at TIMESTAMP NULL COMMENT '激活时间',
    expired_at TIMESTAMP NULL COMMENT '过期时间',
    FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS task (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    status TINYINT NOT NULL DEFAULT 0 COMMENT '0-排队中,1-生成中,2-完成',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS video_generation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL,
    type TINYINT NOT NULL DEFAULT 0 COMMENT '0-人物,1-产品',
    user_prompt TEXT NOT NULL COMMENT '用户提示词',
    system_prompt TEXT COMMENT '系统提示词',
    category VARCHAR(255) COMMENT '分类',
    image_url VARCHAR(1024) NOT NULL COMMENT '输入图片URL',
    video_url VARCHAR(1024) COMMENT '生成视频URL',
    runway_id VARCHAR(255) COMMENT 'Runway任务ID',
    session_id VARCHAR(255) COMMENT 'Runway会话ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES task(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS prompt (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(255) NOT NULL COMMENT '分类',
    category_cn VARCHAR(255) COMMENT '中文分类',
    content TEXT NOT NULL COMMENT '提示词',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS exception_request (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT COMMENT '用户ID',
    ip_address VARCHAR(50) COMMENT 'IP地址',
    request_url VARCHAR(1024) NOT NULL COMMENT '请求URL',
    request_method VARCHAR(10) NOT NULL COMMENT '请求方法',
    request_params TEXT COMMENT '请求参数',
    request_body TEXT COMMENT '请求体',
    error_message TEXT NOT NULL COMMENT '错误信息',
    stack_trace TEXT COMMENT '堆栈跟踪',
    http_status INT COMMENT 'HTTP状态码',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='异常请求记录表';

CREATE TABLE IF NOT EXISTS ai_video (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    prompt TEXT NOT NULL COMMENT '提示词',
    resolution VARCHAR(20) NOT NULL COMMENT '分辨率',
    seconds INT NOT NULL COMMENT '视频时长',
    seed BIGINT NOT NULL COMMENT '随机种子',
    image_url VARCHAR(1024) COMMENT '输入图片URL',
    video_url VARCHAR(1024) COMMENT '生成视频URL',
    status TINYINT NOT NULL DEFAULT 0 COMMENT '状态:0-排队中,1-生成中,2-完成,3-失败',
    is_deleted TINYINT NOT NULL DEFAULT 0 COMMENT '是否删除:0-否,1-是',
    runway_id VARCHAR(255) COMMENT 'Runway任务ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI视频生成记录表';
