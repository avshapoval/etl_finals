#!/bin/bash

# Запуск Airflow
airflow db migrate

# Создание юзеров
airflow users create \
    --username "$_AIRFLOW_WWW_USER_USERNAME" \
    --password "$_AIRFLOW_WWW_USER_PASSWORD" \
    --firstname Peter \
    --lastname Parker \
    --role Admin \
    --email spiderman@superhero.org

# Создание коннектов
airflow connections add 'etl_finals_postgresql' \
    --conn-json '{
        "conn_type": "postgres",
        "login": "'"$POSTGRESQL_APP_USER"'",
        "password": "'"$POSTGRESQL_APP_PASSWORD"'",
        "host": "'"$POSTGRESQL_APP_HOST"'",
        "port": 5432,
        "schema": "'"$POSTGRESQL_APP_DB"'"
    }'

airflow connections add 'etl_finals_mongodb' \
    --conn-json '{
        "conn_type": "mongo",
        "login": "'"$MONGO_USER"'",
        "password": "'"$MONGO_PASSWORD"'",
        "host": "mongo",
        "port": 27017,
        "schema": "'"$MONGO_INITDB_DB"'"
    }'

airflow connections add 'etl_finals_spark' \
    --conn-json '{
        "conn_type": "generic",
        "host": "spark://'"$SPARK_MASTER_HOST"'",
        "port": "'"$SPARK_MASTER_PORT"'",
        "extra": {
            "deploy-mode": "client",
            "spark_binary": "spark3-submit"
        }
    }'

airflow version