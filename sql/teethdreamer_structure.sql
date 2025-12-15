/*
 Navicat Premium Data Transfer

 Source Server         : teeth3d
 Source Server Type    : MySQL
 Source Server Version : 80042 (8.0.42)
 Source Host           : localhost:3306
 Source Schema         : teethdreamer

 Target Server Type    : MySQL
 Target Server Version : 80042 (8.0.42)
 File Encoding         : 65001

 Date: 15/12/2025 16:30:57
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for patients
-- ----------------------------
DROP TABLE IF EXISTS `patients`;
CREATE TABLE `patients`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `patient_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '患者编号，如 P10000123',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '患者姓名',
  `age` int NULL DEFAULT NULL COMMENT '患者年龄',
  `gender` enum('male','female','other') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '患者性别',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '联系电话',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `patient_id`(`patient_id` ASC) USING BTREE,
  INDEX `idx_patient_id`(`patient_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 30 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '患者信息表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for project_data
-- ----------------------------
DROP TABLE IF EXISTS `project_data`;
CREATE TABLE `project_data`  (
  `project_id` bigint NOT NULL AUTO_INCREMENT COMMENT '项目ID',
  `project_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '项目名称',
  `reconstruction_type` enum('全口重建','单口重建','局部重建') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '重建类型',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '项目描述',
  `status` enum('重建中','已完成','失败') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '重建中' COMMENT '项目状态',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `user_id` bigint NULL DEFAULT NULL COMMENT '创建人ID',
  `result_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '重建结果文件路径',
  `progress` tinyint NULL DEFAULT 0 COMMENT '任务进度百分比',
  `error_message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '失败原因说明',
  `finish_time` datetime NULL DEFAULT NULL COMMENT '完成时间',
  `tags` json NULL COMMENT '标签（例如正畸、种植前分析）',
  `priority` tinyint NULL DEFAULT 1 COMMENT '优先级（0=低，1=中，2=高）',
  `patient_id` int NULL DEFAULT NULL COMMENT '关联的患者ID',
  PRIMARY KEY (`project_id`) USING BTREE,
  UNIQUE INDEX `project_name`(`project_name` ASC) USING BTREE,
  INDEX `fk_user`(`user_id` ASC) USING BTREE,
  INDEX `fk_project_patient`(`patient_id` ASC) USING BTREE,
  CONSTRAINT `fk_project_patient` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT,
  CONSTRAINT `fk_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 61 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '牙齿3D重建项目表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for project_images
-- ----------------------------
DROP TABLE IF EXISTS `project_images`;
CREATE TABLE `project_images`  (
  `image_id` bigint NOT NULL AUTO_INCREMENT COMMENT '图片ID',
  `project_id` bigint NOT NULL COMMENT '关联项目ID',
  `file_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'MongoDB GridFS file id',
  `is_cover` tinyint(1) NULL DEFAULT 0 COMMENT '是否封面图',
  `uploaded_at` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
  `patient_id` int NULL DEFAULT NULL COMMENT '关联的患者ID',
  PRIMARY KEY (`image_id`) USING BTREE,
  INDEX `fk_project`(`project_id` ASC) USING BTREE,
  INDEX `idx_patient_id`(`patient_id` ASC) USING BTREE,
  CONSTRAINT `fk_images_patient` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `fk_project` FOREIGN KEY (`project_id`) REFERENCES `project_data` (`project_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 231 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '项目图片表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `user_id` bigint NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `account` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '账号',
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '加密后的密码',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '真实姓名',
  `avatar` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '用户头像URL',
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '邮箱',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '电话号码',
  `address` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '联系地址',
  `department` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '科室',
  `title` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '职称',
  `position` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '职位',
  `license_number` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '执业证号',
  `is_admin` tinyint(1) NULL DEFAULT 0 COMMENT '是否管理员 0-否 1-是',
  `status` tinyint(1) NULL DEFAULT 1 COMMENT '账号状态 1-启用 0-停用',
  `last_login` datetime NULL DEFAULT NULL COMMENT '上次登录时间',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`user_id`) USING BTREE,
  UNIQUE INDEX `account`(`account` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户表' ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;
