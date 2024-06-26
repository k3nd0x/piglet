UPDATE `pig_meta` set `value` = '1.3' where `key` = 'version';

CREATE TABLE IF NOT EXISTS `pig_schedules`(
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `schedule` varchar(32) DEFAULT NULL,
  `o_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_schedule_order` (`o_id`),
  CONSTRAINT `fk_schedule_order` FOREIGN KEY (`o_id`) REFERENCES `pig_orders` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

