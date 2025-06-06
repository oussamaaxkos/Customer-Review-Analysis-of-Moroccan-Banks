from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
import pandas as pd
import json

# Define connections for both databases
transactional_db_conn_id = "transactional_db_conn"
data_warehouse_db_conn_id = "data_warehouse_db_conn"

# Get the previous execution date as a string for the threshold date


def get_previous_date(prev_exec):
    print(f"prev_execution_date is: *{prev_exec}*")
    return f"{prev_exec}"

# Function to extract delta data based on a threshold date


def extract_delta_data(table_name, threshold_date, transactional_db_conn_id, data_warehouse_db_conn_id):
    postgres_hook = PostgresHook(postgres_conn_id=data_warehouse_db_conn_id)
    is_empty = int(postgres_hook.get_pandas_df(
        "select count(*) as e from fact_sales;")['e']) == 0

    postgres_hook = PostgresHook(postgres_conn_id=transactional_db_conn_id)
    if table_name == 'sales' and not is_empty:
        where_clause = f"WHERE sale_date >= '{threshold_date}'"
    else:
        where_clause = ""
    # modifier le query
    query = f""""""
    print(query)
    return postgres_hook.get_pandas_df(query).to_json(orient='records')

# Function to transform data (example: handle missing values)


def transform_data(data):
    # Transforme les données en regroupant les lignes en fonction des colonnes 'customer_id',
    # 'product_id', 'employee_id' et 'discount'. Ensuite, elle agrège les valeurs de la colonne
    # 'quantity' en les additionnant et fait de même pour la colonne 'total_amount'. Enfin,
    # elle réinitialise l'index du DataFrame résultant.
    data = pd.DataFrame(json.loads(data))
    if len(data) == 0:
        return "[]"
    print(data.head(1))
    transformed_data = ...

    transformed_data = transformed_data[[
        'customer_id', 'product_id', 'employee_id', 'quantity', 'discount', 'total_amount']]

    return transformed_data.to_json(orient='records')


def load_data_sales(data, data_warehouse_db_conn_id):
    data = pd.DataFrame(json.loads(data))
    if len(data) == 0:
        return
    postgres_hook = PostgresHook(postgres_conn_id=data_warehouse_db_conn_id)
    sql = f"""
        INSERT INTO fact_sales ({','.join(data.columns)})
        VALUES ({','.join(['%s'] * len(data.columns))});
    """
    parameters = [tuple(row) for row in data.to_numpy()]
    for p in parameters:
        postgres_hook.run(sql, parameters=p)


with DAG(
    dag_id="dag4_etl",
    start_date=datetime(2024, 2, 1),
    schedule_interval=None,  # Run manually or set a schedule
    catchup=False,
) as dag:

    threshold_date = PythonOperator(
        task_id="get_previous_date",
        python_callable=get_previous_date,
        # op_kwargs = {'prev_exec': "{{ prev_execution_date.strftime('%Y-%m-%d %H:%M:%S') }}"}
        op_kwargs={
            'prev_exec': "{{ prev_execution_date.subtract(hours=6).strftime('%Y-%m-%d %H:%M:%S') }}"}
    )

    extract_sales_task = PythonOperator(
        task_id="extract_sales",
        python_callable=extract_delta_data,
        op_args=[
            "sales",
            threshold_date.output,  # Use output of get_previous_date task
            transactional_db_conn_id,
            data_warehouse_db_conn_id
        ],
    )

    transform_sales_task = PythonOperator(
        task_id="transform_sales",
        python_callable=transform_data,
        op_args=[extract_sales_task.output],
    )

    load_sales_task = PythonOperator(
        task_id="load_sales",
        python_callable=load_data_sales,
        op_args=[transform_sales_task.output, data_warehouse_db_conn_id],
    )

threshold_date >> extract_sales_task >> transform_sales_task >> load_sales_task
