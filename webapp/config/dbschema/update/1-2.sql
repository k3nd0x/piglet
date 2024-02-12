RENAME table new_orders to pig_orders;

alter table pig_orders add column id int auto_increment primary key first;

CREATE TABLE IF NOT EXISTS `pig_userbudgets` (
  `user_id` int(11) NOT NULL,
  `budget_id` int(11) NOT NULL,
  `joined` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`user_id`,`budget_id`),
  KEY `budget_id` (`budget_id`),
  CONSTRAINT `budget_id` FOREIGN KEY (`budget_id`) REFERENCES `pig_budgets` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `user_id` FOREIGN KEY (`user_id`) REFERENCES `registered_user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;