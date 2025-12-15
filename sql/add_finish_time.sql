-- 为 project_data 表添加 finish_time 字段
ALTER TABLE `project_data` 
ADD COLUMN `finish_time` datetime NULL DEFAULT NULL COMMENT '完成时间' AFTER `error_message`;

-- 对于已经完成的项目，将 updated_at 作为 finish_time 的初始值
UPDATE `project_data` 
SET `finish_time` = `updated_at` 
WHERE `status` = '已完成' AND `finish_time` IS NULL;
