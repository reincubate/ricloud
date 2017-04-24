
CREATE DATABASE ricloud CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE ricloud;

DROP TABLE IF EXISTS `feed`;

CREATE TABLE `feed` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `service` varchar(16) NOT NULL DEFAULT '' COMMENT 'The service the message was received from.',
  `received` datetime NOT NULL COMMENT 'The time the feed was downloaded.',
  `account_id` int(11) DEFAULT NULL, 
  `device_id` int(11) DEFAULT NULL,
  `device_tag` varchar(100) DEFAULT NULL COMMENT 'An identifier for the device specified by the manufacturer',
  `headers` json DEFAULT NULL,
  `body` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_account_id` (`account_id`),
  KEY `idx_device_id` (`device_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `file`;

CREATE TABLE `file` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `service` varchar(16) NOT NULL DEFAULT '' COMMENT 'The service the message was received from.',
  `received` datetime NOT NULL COMMENT 'The time the file was downloaded.',
  `account_id` int(11) DEFAULT NULL,
  `device_id` int(11) DEFAULT NULL,
  `device_tag` varchar(100) DEFAULT NULL COMMENT 'An identifier for the device specified by the manufacturer',
  `headers` json DEFAULT NULL,
  `location` varchar(250) NOT NULL DEFAULT '' COMMENT 'The location of the file data on disk.',
  `file_id` varchar(4096) DEFAULT NULL COMMENT 'The file ID for cross-reference with feeds.',
  PRIMARY KEY (`id`),
  KEY `idx_account_id` (`account_id`),
  KEY `idx_device_id` (`device_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `message`;

CREATE TABLE `message` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `service` varchar(16) NOT NULL DEFAULT '' COMMENT 'The service the message was received from.',
  `received` datetime NOT NULL COMMENT 'The time the message was received.',
  `account_id` int(11) DEFAULT NULL,
  `device_id` int(11) DEFAULT NULL,
  `device_tag` varchar(100) DEFAULT NULL COMMENT 'An identifier for the device specified by the manufacturer',
  `headers` json DEFAULT NULL,
  `body` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_account_id` (`account_id`),
  KEY `idx_device_id` (`device_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `system`;

CREATE TABLE `system` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `received` datetime NOT NULL COMMENT 'The time the message was received.',
  `headers` json DEFAULT NULL,
  `body` json DEFAULT NULL,
  `message` varchar(200) NOT NULL DEFAULT '',
  `code` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
