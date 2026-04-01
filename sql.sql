CREATE DATABASE ai_customer_service;

USE ai_customer_service;

CREATE TABLE `t_user` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(63) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '用户名称',
    `real_name` VARCHAR(63) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT 'ai小智' COMMENT '用户真实名称',
    `password` VARCHAR(63) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '用户密码',
    `last_login_ip` VARCHAR(63) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT '' COMMENT '最近一次登录IP地址',
    `desc` VARCHAR(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '用户描述',
    `tel` VARCHAR(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '联系电话',
    `mail` VARCHAR(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '邮箱地址',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT ' 创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT ' 更新时间',
    `user_type` TINYINT(4) DEFAULT '1' COMMENT '1-普通用户，2-管理员',
    `is_del` TINYINT(1) DEFAULT '0' COMMENT '是否删除 1-是 0-否',
    PRIMARY KEY (`id`) USING BTREE
) ENGINE=INNODB AUTO_INCREMENT=128 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='用户表';

/**
用户会话表
**/
CREATE TABLE `t_session` (
    `id` BIGINT(32) NOT NULL AUTO_INCREMENT COMMENT '主键',
    `user_id` BIGINT(32) NOT NULL COMMENT '用户id',
    `session_name` VARCHAR(63) DEFAULT '' COMMENT '会话名称',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT ' 创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT ' 更新时间',
    `is_del` TINYINT(1) DEFAULT '0' COMMENT '是否删除 1-是 0-否',
    PRIMARY KEY (`id`)
) ENGINE=INNODB AUTO_INCREMENT=256 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT "用户会话表";

/**
用户会话聊天记录表
**/
CREATE TABLE `t_session_history` (
    `id` BIGINT(32) NOT NULL AUTO_INCREMENT COMMENT '主键',
    `session_id` BIGINT(32) NOT NULL COMMENT '会话id',
    `detail` LONGTEXT COMMENT '聊天详细',
    `history_type` TINYINT(4) DEFAULT '1' COMMENT '1-用户提问，2-ai回复,3-长期记忆上下文(只存前5-8条message)',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT ' 创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT ' 更新时间',
    `is_del` TINYINT(1) DEFAULT '0' COMMENT '是否删除 1-是 0-否',
    PRIMARY KEY (`id`)
) ENGINE=INNODB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT "用户会话聊天记录表";

/**
文件上传记录表
**/
CREATE TABLE `t_file_upload_record` (
    `id` BIGINT(32) NOT NULL AUTO_INCREMENT COMMENT '主键',
    `user_id` BIGINT(32) NOT NULL COMMENT '用户id',
    `file_name` VARCHAR(128) COMMENT '原始文件名称',
    `local_file_name` VARCHAR(128) COMMENT '本地文件名称',
    `local_file_path` VARCHAR(256) COMMENT '本地文件路径',
    `state` TINYINT(1) DEFAULT '2' COMMENT '文件状态 1-已加载 2-加载失败',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT ' 创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `is_del` TINYINT(1) DEFAULT '0' COMMENT '是否删除 1-是 0-否',
    PRIMARY KEY (`id`)
) ENGINE=INNODB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT "文件上传记录表";

