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

 Date: 09/12/2025 15:08:11
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
-- Records of patients
-- ----------------------------
INSERT INTO `patients` VALUES (2, 'P10000', '张三', 12, 'male', NULL, '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (3, 'P10001', '李四', 16, 'female', NULL, '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (4, 'P10002', '王五', 20, 'male', NULL, '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (5, 'P10003', '赵六', 24, 'female', NULL, '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (6, 'P10004', '孙七', 30, 'male', NULL, '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (7, 'P10005', '周八', 10, 'female', NULL, '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (8, 'P10006', '吴九', 7, 'male', NULL, '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (9, 'P10007', '郑十', 14, 'female', NULL, '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (10, 'P10008', '钱一', 18, 'male', '13800000001', '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (11, 'P10009', '孙二', 22, 'female', '13800000002', '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (12, 'P10010', '周三', 35, 'male', '13800000003', '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (13, 'P10011', '吴四', 28, 'female', '13800000004', '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (14, 'P10012', '郑五', 41, 'male', '13800000005', '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (15, 'P10013', '王六', 33, 'female', '13800000006', '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (16, 'P10014', '冯七', 26, 'male', '13800000007', '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (17, 'P10015', '陈八', 52, 'female', '13800000008', '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (18, 'P10016', '褚九', 19, 'male', '13800000009', '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (19, 'P10017', '卫十', 47, 'female', '13800000010', '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (20, 'P10018', '蒋十一', 29, 'male', '13800000011', '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (21, 'P10019', '沈十二', 23, 'female', '13800000012', '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (22, 'P10020', '韩十三', 38, 'male', '13800000013', '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (23, 'P10021', '杨十四', 16, 'female', '13800000014', '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (24, 'P10022', '朱十五', 45, 'male', '13800000015', '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (25, 'P10023', '秦十六', 31, 'female', '13800000016', '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (26, 'P10024', '尤十七', 55, 'male', '13800000017', '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (27, 'P10025', '许十八', 27, 'female', '13800000018', '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (28, 'P10026', '何十九', 12, 'male', '13800000019', '2025-12-04 09:30:40', '2025-12-04 09:30:40');
INSERT INTO `patients` VALUES (29, 'P10027', '吕二十', 40, 'female', '13800000020', '2025-12-04 09:30:40', '2025-12-04 09:30:40');

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
) ENGINE = InnoDB AUTO_INCREMENT = 60 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '牙齿3D重建项目表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of project_data
-- ----------------------------
INSERT INTO `project_data` VALUES (55, 'P10000-3', '全口重建', '', '已完成', '2025-12-04 16:15:08', '2025-12-08 11:21:15', 4, NULL, 0, NULL, '2025-12-04 16:49:58', NULL, 1, 2);
INSERT INTO `project_data` VALUES (56, 'P10004-1', '全口重建', '', '已完成', '2025-12-04 16:57:06', '2025-12-08 11:21:15', 4, NULL, 0, NULL, '2025-12-04 17:15:22', NULL, 1, 6);
INSERT INTO `project_data` VALUES (57, 'P10005-1', '全口重建', '', '已完成', '2025-12-04 17:02:56', '2025-12-08 11:21:15', 4, NULL, 0, NULL, '2025-12-04 17:15:22', NULL, 1, 7);
INSERT INTO `project_data` VALUES (58, 'P10025-1', '全口重建', '', '已完成', '2025-12-08 11:07:21', '2025-12-08 11:21:15', 4, NULL, 0, NULL, '2025-12-08 11:17:29', NULL, 1, 27);
INSERT INTO `project_data` VALUES (59, 'P10008-1', '全口重建', '', '已完成', '2025-12-08 11:24:13', '2025-12-08 11:34:41', 4, NULL, 0, NULL, '2025-12-08 11:34:41', NULL, 1, 10);

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
) ENGINE = InnoDB AUTO_INCREMENT = 226 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '项目图片表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of project_images
-- ----------------------------
INSERT INTO `project_images` VALUES (201, 55, '6931430b9e8b7fcf1079f0b2', 1, '2025-12-04 16:15:08', NULL);
INSERT INTO `project_images` VALUES (202, 55, '6931430c9e8b7fcf1079f0c4', 0, '2025-12-04 16:15:08', NULL);
INSERT INTO `project_images` VALUES (203, 55, '6931430c9e8b7fcf1079f0d8', 0, '2025-12-04 16:15:08', NULL);
INSERT INTO `project_images` VALUES (204, 55, '6931430c9e8b7fcf1079f0e8', 0, '2025-12-04 16:15:08', NULL);
INSERT INTO `project_images` VALUES (205, 55, '6931430c9e8b7fcf1079f0f7', 0, '2025-12-04 16:15:08', NULL);
INSERT INTO `project_images` VALUES (206, 56, '69314ce29e8b7fcf1079f10a', 1, '2025-12-04 16:57:06', NULL);
INSERT INTO `project_images` VALUES (207, 56, '69314ce29e8b7fcf1079f11c', 0, '2025-12-04 16:57:06', NULL);
INSERT INTO `project_images` VALUES (208, 56, '69314ce29e8b7fcf1079f130', 0, '2025-12-04 16:57:06', NULL);
INSERT INTO `project_images` VALUES (209, 56, '69314ce29e8b7fcf1079f140', 0, '2025-12-04 16:57:06', NULL);
INSERT INTO `project_images` VALUES (210, 56, '69314ce29e8b7fcf1079f14f', 0, '2025-12-04 16:57:07', NULL);
INSERT INTO `project_images` VALUES (211, 57, '69314e409e8b7fcf1079f162', 1, '2025-12-04 17:02:56', NULL);
INSERT INTO `project_images` VALUES (212, 57, '69314e409e8b7fcf1079f174', 0, '2025-12-04 17:02:56', NULL);
INSERT INTO `project_images` VALUES (213, 57, '69314e409e8b7fcf1079f188', 0, '2025-12-04 17:02:56', NULL);
INSERT INTO `project_images` VALUES (214, 57, '69314e409e8b7fcf1079f198', 0, '2025-12-04 17:02:56', NULL);
INSERT INTO `project_images` VALUES (215, 57, '69314e409e8b7fcf1079f1a7', 0, '2025-12-04 17:02:57', NULL);
INSERT INTO `project_images` VALUES (216, 58, '693640e865051ab81d349d4e', 1, '2025-12-08 11:07:21', NULL);
INSERT INTO `project_images` VALUES (217, 58, '693640e865051ab81d349d60', 0, '2025-12-08 11:07:21', NULL);
INSERT INTO `project_images` VALUES (218, 58, '693640e965051ab81d349d74', 0, '2025-12-08 11:07:21', NULL);
INSERT INTO `project_images` VALUES (219, 58, '693640e965051ab81d349d84', 0, '2025-12-08 11:07:21', NULL);
INSERT INTO `project_images` VALUES (220, 58, '693640e965051ab81d349d93', 0, '2025-12-08 11:07:21', NULL);
INSERT INTO `project_images` VALUES (221, 59, '693644dd548bba6cb4164145', 1, '2025-12-08 11:24:13', NULL);
INSERT INTO `project_images` VALUES (222, 59, '693644dd548bba6cb4164157', 0, '2025-12-08 11:24:14', NULL);
INSERT INTO `project_images` VALUES (223, 59, '693644dd548bba6cb416416b', 0, '2025-12-08 11:24:14', NULL);
INSERT INTO `project_images` VALUES (224, 59, '693644dd548bba6cb416417b', 0, '2025-12-08 11:24:14', NULL);
INSERT INTO `project_images` VALUES (225, 59, '693644dd548bba6cb416418a', 0, '2025-12-08 11:24:14', NULL);

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

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO `user` VALUES (4, 'user', '$pbkdf2-sha256$29000$59ybc07pvXfufY.xdi7FuA$wMHCDtpn9kCvTfVHWeCEDjfLnVOttTSOWVe/dSyPIos', 'user', NULL, '18936361958@163.com', NULL, NULL, NULL, NULL, NULL, NULL, 0, 1, NULL, NULL, NULL);

SET FOREIGN_KEY_CHECKS = 1;
