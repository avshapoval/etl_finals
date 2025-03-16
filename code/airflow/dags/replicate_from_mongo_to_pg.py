from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.mongo.hooks.mongo import MongoHook

from scripts.helpers.airflow_common import get_pg_connection_uri, get_mongo_connection_uri 

# Константы
COLLECTIONS_TABLES_MAPPING = [
    ("UserSessions", "user_sessions"),
    ("ProductPriceHistory", "product_price_history"),
    ("EventLogs", "event_logs"),
    ("SupportTickets", "support_tickets"),
    ("UserRecommendations", "user_recommendations"),
    ("ModerationQueue", "moderation_queue"),
    ("SearchQueries", "search_queries")
]

JARS = (
    "/opt/airflow/spark/jars/postgresql-42.2.18.jar,"
    #"/opt/airflow/spark/jars/mongo-driver-sync_5.3.1.jar,"
    #"/opt/airflow/spark/jars/mongo-spark-connector.jar"
)

PYSPARK_SCRIPT_PATH = '/opt/airflow/scripts/pyspark_scripts/mongo_to_pg_replication.py'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'catchup': False
}

with DAG(
    'mongo_to_pg_full_replication',
    default_args=default_args,
    description='Полная репликация данных из MongoDB в PostgreSQL',
    schedule_interval=timedelta(days=1),
    max_active_runs=1
) as dag:
    
    start = EmptyOperator(task_id='start')
    finish = EmptyOperator(task_id='finish')

    # Получение параметров подключения
    pg_hook = PostgresHook.get_connection('etl_finals_postgresql')
    pg_uri = get_pg_connection_uri(pg_hook)
    pg_driver = "org.postgresql.Driver"

    mongo_hook = MongoHook.get_connection('etl_finals_mongodb')
    mongo_uri = get_mongo_connection_uri(mongo_hook)

    for collection, tbl_name in COLLECTIONS_TABLES_MAPPING:
        spark_task = SparkSubmitOperator(
            task_id=f'replicate_{collection.lower()}',
            application=PYSPARK_SCRIPT_PATH,
            conn_id='etl_finals_spark',
            application_args=[
                '--mongo_uri', mongo_uri,
                '--pg_uri', pg_uri,
                '--pg_driver', pg_driver,
                '--collection', collection,
                '--schema', 'stg',
                "--pg_table_name", tbl_name
            ],
            conf={
                "spark.driver.memory": "700m",
                "spark.executor.memory": "700m"
            },
            jars=JARS,
            packages="org.mongodb.spark:mongo-spark-connector_2.12:10.4.1",
            executor_cores=1,
            executor_memory='700m'
        )

        start >> spark_task >> finish