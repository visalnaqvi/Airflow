from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from scripts.compression_dag.S1_checks import update_groups_last_image_timestamp
from scripts.compression_dag.S1_table_checks import ensure_tables_exist
from scripts.compression_dag.S3_update_group_heating_to_warm import update_groups_to_warm

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
    dag_id="compression_dag",
    default_args=default_args,
    description="A simple DAG with PythonOperator",
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["example"],
) as dag:

    # Debug task to check Node.js installation and module resolution
    debug_node = BashOperator(
        task_id="debug_node_installation",
        bash_command="""
        echo "=== Environment Debug ==="
        echo "PATH: $PATH"
        echo "Current working directory: $(pwd)"
        echo "User: $(whoami)"
        echo "=== Node.js Version ==="
        node --version
        npm --version
        echo "=== Directory Structure Check ==="
        echo "Contents of /opt/airflow/dags/scripts/:"
        ls -la /opt/airflow/dags/scripts/ || echo "scripts directory not found"
        echo "Contents of /opt/airflow/dags/scripts/compression_dag/:"
        ls -la /opt/airflow/dags/scripts/compression_dag/ || echo "compression_dag directory not found"
        echo "=== Package.json Check ==="
        cd /opt/airflow/dags/scripts/compression_dag
        echo "Current directory: $(pwd)"
        cat package.json || echo "package.json not found"
        echo "=== Node Modules Check ==="
        if [ -d "node_modules" ]; then
            echo "node_modules directory exists"
            ls -la node_modules/ | head -20
            echo "=== Specific module directories ==="
            ls -la node_modules/pg || echo "pg module directory not found"
            ls -la node_modules/axios || echo "axios module directory not found"
            ls -la node_modules/sharp || echo "sharp module directory not found"
            ls -la node_modules/firebase-admin || echo "firebase-admin module directory not found"
        else
            echo "node_modules directory does not exist"
            echo "Attempting to install modules now..."
            npm install
        fi
        echo "=== NPM List ==="
        npm list --depth=0 || echo "No local packages found"
        echo "=== Module Resolution Test ==="
        node -e "console.log('pg module:', require.resolve('pg'))" || echo "pg module not found"
        node -e "console.log('axios module:', require.resolve('axios'))" || echo "axios module not found"
        node -e "console.log('sharp module:', require.resolve('sharp'))" || echo "sharp module not found"
        node -e "console.log('firebase-admin module:', require.resolve('firebase-admin'))" || echo "firebase-admin module not found"
        """
    )

    ensure_tables_exist_task = PythonOperator(
        task_id="ensure_tables_exist",
        python_callable=ensure_tables_exist,
        provide_context=True,
    )
    
    update_groups_last_image_timestamp_task = PythonOperator(
        task_id="update_groups_last_image_timestamp",
        python_callable=update_groups_last_image_timestamp,
        provide_context=True,
    )
    
    # Fixed processImages task - change to the correct directory first
    processImages = BashOperator(
        task_id="processImages",
        bash_command="cd /opt/airflow/dags/scripts/compression_dag && node S2_F1_sharp_hot_to_warm.js"    )
    
    update_groups_to_warm_task = PythonOperator(
        task_id="update_groups_to_warm",
        python_callable=update_groups_to_warm,
        provide_context=True,
    )
    
    # Set dependencies
    debug_node >> ensure_tables_exist_task >> update_groups_last_image_timestamp_task >> processImages >> update_groups_to_warm_task