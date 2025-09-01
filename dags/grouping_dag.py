from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from scripts.grouping_dag.S5_assign_face_quality_score import assign_face_quality_score
from scripts.grouping_dag.S6_F1_group_emb_using_db import groupping
from scripts.grouping_dag.S7_F1_insert_person_table import sync_persons
from scripts.grouping_dag.S8_F1_generate_centroidds import generate_centroids
from scripts.grouping_dag.S9_F1_centroid_matching import centroid_matching

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
    dag_id="grouping_dag",
    default_args=default_args,
    description="A simple DAG with PythonOperator",
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["example"],
) as dag:

   
    assign_face_quality_score_step = PythonOperator(
        task_id="assign_face_quality_score",
        python_callable=assign_face_quality_score,
        provide_context=True,
    )
    
    groupping_step = PythonOperator(
        task_id="groupping",
        python_callable=groupping,
        provide_context=True,
    )
    
    sync_persons_step = PythonOperator(
        task_id="sync_persons",
        python_callable=sync_persons,
        provide_context=True,
    )
    
    generate_centroids_step = PythonOperator(
        task_id="generate_centroids",
        python_callable=generate_centroids,
        provide_context=True,
    )
    
    centroid_matching_step = PythonOperator(
        task_id="centroid_matching",
        python_callable=centroid_matching,
        provide_context=True,
    )
    
    assign_face_quality_score_step >> groupping_step >> sync_persons_step >> generate_centroids_step >> centroid_matching_step