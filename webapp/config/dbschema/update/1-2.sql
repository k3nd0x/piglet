RENAME table new_orders to pig_orders;

alter table pig_orders add column id int auto_increment primary key first;
