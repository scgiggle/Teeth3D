/*
 Navicat Premium Data Transfer

 Source Server         : difnagzhi
 Source Server Type    : MySQL
 Source Server Version : 80042 (8.0.42)
 Source Host           : localhost:3306
 Source Schema         : teeth_reconstruction

 Target Server Type    : MySQL
 Target Server Version : 80042 (8.0.42)
 File Encoding         : 65001

 Date: 25/09/2025 16:23:18
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

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
  `tags` json NULL COMMENT '标签（例如正畸、种植前分析）',
  `priority` tinyint NULL DEFAULT 1 COMMENT '优先级（0=低，1=中，2=高）',
  PRIMARY KEY (`project_id`) USING BTREE,
  UNIQUE INDEX `project_name`(`project_name` ASC) USING BTREE,
  INDEX `fk_user`(`user_id` ASC) USING BTREE,
  CONSTRAINT `fk_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '牙齿3D重建项目表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of project_data
-- ----------------------------

SET FOREIGN_KEY_CHECKS = 1;
