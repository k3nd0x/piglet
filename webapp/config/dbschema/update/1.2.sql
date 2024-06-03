RENAME TABLE IF EXISTS new_orders TO pig_orders;
ALTER TABLE pig_orders ADD COLUMN IF NOT EXISTS id INT AUTO_INCREMENT PRIMARY KEY FIRST;

CREATE TABLE IF NOT EXISTS `pig_meta` (
    `key` VARCHAR(255),
    `value` VARCHAR(255),
    PRIMARY KEY (`key`)
);

INSERT IGNORE INTO `pig_meta` (`key`, `value`) VALUES ('version', '1.2');

CREATE TABLE IF NOT EXISTS `pig_userbudgets` (
    `user_id` INT(11) NOT NULL,
    `budget_id` INT(11) NOT NULL,
    `joined` TINYINT(4) DEFAULT NULL,
    PRIMARY KEY (`user_id`, `budget_id`),
    KEY `budget_id` (`budget_id`),
    CONSTRAINT `budget_id` FOREIGN KEY (`budget_id`) REFERENCES `pig_budgets` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
    CONSTRAINT `user_id` FOREIGN KEY (`user_id`) REFERENCES `registered_user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
);

INSERT IGNORE INTO pig_notitype VALUES (3, "budget", "Budget");

INSERT IGNORE INTO pig_notiobj VALUES (3, 'joined', 'joined'), (4, 'shared', 'shared');

ALTER TABLE pig_notisettings ADD CONSTRAINT IF NOT EXISTS unique_line_constraint UNIQUE (user_id, notiobj, notitype, mail, web);
