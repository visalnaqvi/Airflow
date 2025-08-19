from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Default DAG arguments
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def main():
    print("yo")
    
# Define the DAG
with DAG(
    dag_id="apple_extraction_dag",
    default_args=default_args,
    description="A simple DAG with PythonOperator",
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["example"],
) as dag:

   
    extraction = PythonOperator(
        task_id="extraction",
        python_callable=main,
        provide_context=True,
    )
    
    
    extraction