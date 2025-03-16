from datetime import datetime

from airflow import DAG
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators.empty import EmptyOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator, BranchSQLOperator


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'retries': 1,
}

STG_PG_SCHEMA = "stg"
MARTS_PG_SCHEMA = "cdm"
MARTS_TABLE_DDL_FILE_MAPPING = {
    "moderation_stats": "/sql/marts_ddl/moderation_stats.sql",
    "product_price_dynamics": "/sql/marts_ddl/product_price_dynamics.sql",
    "user_session_analysis": "/sql/marts_ddl/user_session_analysis.sql"
}
PG_CONN_ID = 'etl_finals_postgresql'
FILEPATH_PREFIX = '/opt/airflow/scripts'

with DAG(
    'cdm_materialized_views_refresh',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    tags=['cdm', 'materialized_views'],
    template_searchpath=FILEPATH_PREFIX
) as dag:

    start = EmptyOperator(task_id='start')
    end = EmptyOperator(task_id='end')

    for mv_name, mv_ddl_filepath in MARTS_TABLE_DDL_FILE_MAPPING.items():

        # Проверяем, есть ли mv. Если да - переходим к обновлению, если нет - сначала создаем.
        check_task = BranchSQLOperator(
            task_id=f'check_{mv_name}',
            conn_id=PG_CONN_ID,
            sql=f"sql/marts_common/check_mart_exists.sql",
            params={"mat_view_name": mv_name, "marts_schema": MARTS_PG_SCHEMA},
            follow_task_ids_if_true=f'refresh_{mv_name}',
            follow_task_ids_if_false=f'create_{mv_name}'
        )

        # Создание mv
        create_task = SQLExecuteQueryOperator(
            task_id=f'create_{mv_name}',
            sql=mv_ddl_filepath,
            conn_id=PG_CONN_ID,
            params={"mat_view_name": mv_name, "marts_schema": MARTS_PG_SCHEMA, "stg_schema": STG_PG_SCHEMA}
        )

        # Обновление mv
        refresh_task = SQLExecuteQueryOperator(
            task_id=f'refresh_{mv_name}',
            sql=f"sql/marts_common/refresh_mart.sql",
            conn_id=PG_CONN_ID,
            params={"mat_view_name": mv_name, "marts_schema": MARTS_PG_SCHEMA},
            trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS
        )

        # Оркестрация задач
        start >> check_task
        check_task >> [create_task, refresh_task]
        create_task >> refresh_task
        refresh_task >> end
