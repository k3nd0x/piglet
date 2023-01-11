# piglet :pig:

Simple Webapp to manage and administrate budgets in a household

# About

This project is an easy webapp to manage your budget. It comes with an lightweight webinterface and an api.
You can easily add, categorize and compare your expenditures, individualize your categories and profile. 

- All the data is stored at the server in a mysql database. Passwords are hashed and salted and can only be decrypted by the the creator.
- A user can only read his own data. It is not possible (over the webinterface/api) to read data of other users apart from the budget is shared.

# Deployment
You can use the docker-compose.yml to create both containers (piglet, mariadb). 
At the first startup of piglet all relevant data will be created in the database.

Following ENV variables are possible:
| ENV variable  | description | defaults | required |
| -- | -- | -- | -- |
| MYSQL_USER  | User for the piglet database | piglet | :x:
| MYSQL_DATABASE  | Name of the piglet database | piglet | :x:
| MYSQL_HOST | Hostname or IP Address of the databasehost | database | :x:
| MYSQL_PASSWORD | Password for the piglet database user | None | :white_check_mark:
| FLASK_SECRET_KEY | Secret key for the flask session | None (will be generated at first startup) | :x:
