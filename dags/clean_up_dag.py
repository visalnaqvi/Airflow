from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from scripts.cleanup_dag.S1_clear_images import cleanup_expired_images
from scripts.cleanup_dag.S2_delete_group import cleanup_expired_groups
from scripts.cleanup_dag.S3_firebase_cleanup import firebase_cleanup
from scripts.cleanup_dag.S6_delete_non_elite_group_images_from_firebase import cleanup_non_elite_files

# Default DAG arguments
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Define the DAG
with DAG(
    dag_id="clean_up_dag",
    default_args=default_args,
    description="A simple DAG with PythonOperator",
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["example"],
) as dag:

   
    cleanup_expired_images_step = PythonOperator(
        task_id="cleanup_expired_images",
        python_callable=cleanup_expired_images,
        provide_context=True,
    )
    
    cleanup_expired_groups_step = PythonOperator(
        task_id="cleanup_expired_groups",
        python_callable=cleanup_expired_groups,
        provide_context=True,
    )
    
    firebase_cleanup_step = PythonOperator(
        task_id="firebase_cleanup",
        python_callable=firebase_cleanup,
        provide_context=True,
    )
    
    cleanup_non_elite_files_step = PythonOperator(
        task_id="cleanup_non_elite_files",
        python_callable=cleanup_non_elite_files,
        provide_context=True,
    )
    
    cleanup_expired_images_step >> cleanup_expired_groups_step >> firebase_cleanup_step >> cleanup_non_elite_files_step