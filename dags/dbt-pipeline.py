from datetime import datetime, timedelta

from airflow.models import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.operators.bash import BashOperator


from scripts.transactions import fetch_product_data, generate_fake_transaction
from scripts.files import upload_to_s3

# -------------------- FUNCTIONS -------------------- #

def generate_transactions(**kwargs):
    amount = 10
    ti = kwargs['ti']  # Access the XCom Task Instance
    max_customer_id=ti.xcom_pull(task_ids='fetch_max_customer_id', key='return_value')
    generate_fake_transaction(amount, max_customer_id)

# -------------------- DAG -------------------- #

default_args = {
    'owner': 'airflow',
    'email': ['shayne@shaynelussier.com'],
    'email_on_failure': False, # set to True
    "depends_on_past": False,
    'retries': 0,
    "retry_delay": timedelta(seconds=30)
}


with DAG(
    dag_id='DAG',
    start_date=datetime(2023, 12, 1),
    schedule_interval= '0 20 * * *', # 8 pm EST,
    catchup=False,
    default_args=default_args,
    description='Perform ELT on transaction JSON data into Snowflake for downstream analytics',
) as dag:

    fetch_s3_product_data = PythonOperator(
        task_id='fetch_s3_product_data',
        python_callable=fetch_product_data,
        do_xcom_push=True,
        dag=dag,
    )

    fetch_max_customer_id = SnowflakeOperator(
        task_id='fetch_max_customer_id',
        sql="SELECT MAX(customer_id) AS max_customer_id FROM analytics.customers_dim",
        snowflake_conn_id='snowflake_analytics_conn',
        do_xcom_push=True,
        dag=dag,
    )

    generate_transactions = PythonOperator(
        task_id='generate_transactions',
        python_callable=generate_transactions,
        provide_context=True,
        trigger_rule='all_success',
        dag=dag,
    )

    upload_to_s3 = PythonOperator(
        task_id='upload_to_s3',
        python_callable=upload_to_s3,
        dag=dag,
    )

    create_staging_table = SnowflakeOperator(
        task_id='create_staging_table',
        snowflake_conn_id='snowflake_staging_conn',
        sql="""
            CREATE OR REPLACE TABLE staging.raw_data (
            id STRING,
            date STRING,
            customer OBJECT,
            items ARRAY 
            );
            """,
        dag=dag
    )

    copy_raw_data = SnowflakeOperator(
    task_id='copy_raw_data',
    snowflake_conn_id='snowflake_staging_conn',
    sql="""
        COPY INTO "STORE"."STAGING"."RAW_DATA"
        FROM @s3_data_pipeline_repo
        FILES=('transactions.json')
        FILE_FORMAT=(
            TYPE=JSON,
            STRIP_OUTER_ARRAY=TRUE,
            REPLACE_INVALID_CHARACTERS=TRUE,
            DATE_FORMAT=AUTO,
            TIME_FORMAT=AUTO,
            TIMESTAMP_FORMAT=AUTO
        )
        MATCH_BY_COLUMN_NAME=CASE_INSENSITIVE
        ON_ERROR=ABORT_STATEMENT
        """,
        dag=dag,
    )

    populate_customers_dim = BashOperator(
        task_id='populate_customers_dim',
        bash_command='dbt run --models store.customers_dim.* --profiles-dir ./',
        cwd='/opt/airflow/dbt',
        dag=dag,
    )

    populate_transactions_fact = BashOperator(
        task_id='populate_transactions_fact',
        bash_command='dbt run --models store.transactions_fact.* --profiles-dir ./',
        cwd='/opt/airflow/dbt',
        dag=dag,
    )

    # Define the task dependency
    [fetch_s3_product_data, fetch_max_customer_id] >> generate_transactions >> upload_to_s3 >> create_staging_table
    create_staging_table >> copy_raw_data >> [populate_customers_dim, populate_transactions_fact]