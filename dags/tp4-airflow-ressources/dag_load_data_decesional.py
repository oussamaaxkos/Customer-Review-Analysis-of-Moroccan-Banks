from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import pandas as pd
import json, random
import psycopg2


# Define connections for both databases
transactional_db_conn_id = "transactional_db_conn"


def generate_sales_commands():
    postgres_hook = PostgresHook(postgres_conn_id=transactional_db_conn_id)

    num_customers = 500
    num_products = 50
    num_employees = 5
    price = 100

    num_sales = random.randint(1, 5)  # Generate a random number of sales records
    print(f"++++ Inserting {num_sales=} new records ++++")
    for _ in range(num_sales):
        customer_id = random.randint(1, num_customers)
        product_id = random.randint(1, num_products)
        employee_id = random.randint(1, num_employees)
        quantity = random.randint(1, 5)
        sale_date = datetime.now() - timedelta(seconds=random.randint(1, 10))
        discount = round(random.uniform(0, 0.2), 2)
        total_amount = round(price * quantity * (1 - discount), 2)

        sql = 'INSERT INTO sales (customer_id, product_id, employee_id, quantity, sale_date, discount, total_amount) VALUES (%s, %s, %s, %s, %s, %s, %s)'
        
        postgres_hook.run(sql, parameters=(customer_id, product_id, employee_id, quantity, sale_date, discount, total_amount))


with DAG(
    dag_id="dag_load_data_dec_",
    start_date=datetime(2024, 2, 1),
    schedule_interval="1 * * * *",  # every one minutes
    catchup=False,
) as dag:

    threshold_date = PythonOperator(
        task_id="generate_sales_commands",
        python_callable=generate_sales_commands
    )