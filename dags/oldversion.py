# from airflow import DAG
# from airflow.operators.python_operator import PythonOperator
# from airflow.utils.dates import days_ago
# from sqlalchemy import create_engine
# from sqlalchemy.exc import SQLAlchemyError
# import time
# import pandas as pd
# from datetime import datetime
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import NoSuchElementException, TimeoutException
# from webdriver_manager.chrome import ChromeDriverManager

# # Path to ChromeDriver
# # chrome_driver_path = "/home/osama/airflow/chromdriver/chromedriver.exe"
# chrome_driver_path = ChromeDriverManager().install()

# # List of banks to scrape
# bank_urls = [
#     "https://www.google.com/maps/place/BANK+OF+AFRICA,+Agence+Abdelmoumen,+Casablanca./@33.5265726,-7.7316491,13z/data=!4m13!1m3!2m2!1sBMCE+Bank+of+Africa!6e2!3m8!1s0xda7d2b1401cddab:0xa09ec03c31179e50!8m2!3d33.5677444!4d-7.6264518!9m1!1b1!15sChNCTUNFIEJhbmsgb2YgQWZyaWNhkgEEYmFua-ABAA!16s%2Fg%2F1tklrxp2!5m1!1e1?entry=ttu&g_ep=EgoyMDI1MDMwNC4wIKXMDSoJLDEwMjExNDUzSAFQAw%3D%3D",
#     "https://www.google.com/maps/place/%D8%A8%D9%86%D9%83+%D8%A3%D9%81%D8%B1%D9%8A%D9%82%D9%8A%D8%A7%E2%80%AD/@33.5265726,-7.7316491,13z/data=!4m13!1m3!2m2!1sBMCE+Bank+of+Africa!6e2!3m8!1s0xda62cb2e1b355d9:0x92b1eb404df1b850!8m2!3d33.5563893!4d-7.6848036!9m1!1b1!15sChNCTUNFIEJhbmsgb2YgQWZyaWNhkgEEYmFua-ABAA!16s%2Fg%2F11crv4pc1x!5m1!1e1?entry=ttu&g_ep=EgoyMDI1MDMwNC4wIKXMDSoJLDEwMjExNDUzSAFQAw%3D%3D"
# ]

# # Function to initialize the WebDriver
# def initialize_driver():
#     options = Options()
#     options.add_argument("--headless")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     service = Service(chrome_driver_path)
#     driver = webdriver.Chrome(service=service, options=options)
#     return driver

# # Function to scroll the page
# # def scroll_page(driver):
# #     for _ in range(10):  # Number of scrolls
# #         driver.execute_script("window.scrollBy(0, 400);")
# #         time.sleep(2)

# # Function to convert "X years ago" into a specific year
# def convert_relative_date(relative_date):
#     now = datetime.now()
#     try:
#         parts = relative_date.split()
#         if len(parts) >= 3:  # Handle years
#             if parts[3] == "un":
#                 parts[3] = "1"
#             years_ago = int(parts[3])
#             return str(now.year - years_ago)  # Calculate the year
#         elif "months" in relative_date:  # Handle months
#             return str(now.year)
#         elif "days" in relative_date:  # Handle days
#             return str(now.year)
#         else:
#             return "N/A"
#     except (IndexError, ValueError):
#         return "N/A"

# # Task to create the table if it doesn't exist
# def create_table_if_not_exists():
#     sql_alchemy_conn = "postgresql+psycopg2://airflow_user:pass1234@localhost:5432/airflow_db"
#     engine = create_engine(sql_alchemy_conn)
#     create_table_query = """
#     CREATE TABLE IF NOT EXISTS bank_agency_reviews (
#         id SERIAL PRIMARY KEY,
#         bank_name VARCHAR(255),
#         address TEXT,
#         review TEXT,
#         rating VARCHAR(10),
#         review_date VARCHAR(20)
#     );
#     """
#     try:
#         with engine.connect() as connection:
#             connection.execute(create_table_query)
#             print("✅ Table 'bank_agency_reviews' checked/created successfully.")
#     except SQLAlchemyError as e:
#         print(f"⚠️ Error creating table: {e}")

# # Task to extract data
# def extract_data(**kwargs):
#     driver = initialize_driver()  # Initialize WebDriver inside the task
#     all_data = []
#     for index, url in enumerate(bank_urls, start=1):
#         print(f"🔍 Scraping de l'URL {index}: {url}")
#         driver.get(url)
#         time.sleep(5)  # Laisser la page se charger

#         # scroll_page()  # Scroller pour charger les avis

#         # 🔹 Extraire les avis et dates avant de cliquer sur "Présentation"
#         try:
#             review_elements = driver.find_elements(By.CSS_SELECTOR, "span.wiI7pd")
#             date_elements = driver.find_elements(By.CSS_SELECTOR, "span.rsqaWe")

#             print(f"🔍 Nombre d'avis trouvés : {len(review_elements)}")

#             # 🔹 Stocker temporairement les avis et dates
#             reviews = [review.text.strip() for review in review_elements]
#             dates = [convert_relative_date(date.text.strip()) for date in date_elements]

#         except Exception as e:
#             print(f"⚠️ Erreur lors de l'extraction des avis : {e}")
#             continue

#         # 🔹 Cliquer sur le div "Présentation" pour révéler l'adresse et le rating
#         try:
#             presentation_div = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "div.LRkQ2"))
#             )
#             presentation_div.click()
#             time.sleep(2)  # Attendre que l'adresse et le rating soient chargés
#         except TimeoutException:
#             print("⚠️ Impossible de cliquer sur le div de présentation")
#             continue

#         # 🔹 Récupérer le nom de la banque après avoir cliqué sur "Présentation"
#         try:
#             bank_name_element = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf.lfPIob"))
#             )
#             bank_name = bank_name_element.text.strip()
#         except TimeoutException:
#             bank_name = f"Banque {index}"

#         print(f"📌 Nom de la banque détecté : {bank_name}")

#         # 🔹 Récupérer l'adresse de la banque
#         try:
#             address_element = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "div.Io6YTe.fontBodyMedium.kR99db.fdkmkc"))
#             )
#             address = address_element.text.strip()
#         except TimeoutException:
#             address = "Non trouvée"

#         print(f"📌 Adresse de la banque détectée : {address}")

#         # 🔹 Récupérer le rating après avoir cliqué sur "Présentation"
#         try:
#             rating_element = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "div.F7nice span[aria-hidden='true']"))
#             )
#             rating = rating_element.text.strip()
#         except TimeoutException:
#             rating = "N/A"

#         print(f"📌 Note de la banque détectée : {rating}")

#         # 🔹 Stocker les données dans une liste
#         for i in range(len(reviews)):
#             try:
#                 all_data.append({
#                     "Nom de la Banque": bank_name,
#                     "Adresse": address,
#                     "Avis": reviews[i],
#                     "Note": rating,  # Use the same rating for all reviews
#                     "Date": dates[i] if i < len(dates) else "N/A"  # Only the year (e.g., 2020)
#                 })
#             except Exception as e:
#                 print(f"⚠️ Erreur lors du traitement d'un avis : {e}")

#     driver.quit()  # Close the WebDriver after the task
#     driver.close()  # Close the WebDriver after the task
#     kwargs['ti'].xcom_push(key='scraped_data', value=all_data)

# # Task to insert data into the database
# def insert_data_into_db(**kwargs):
#     ti = kwargs['ti']
#     scraped_data = ti.xcom_pull(task_ids='extract_data', key='scraped_data')
#     df = pd.DataFrame(scraped_data)
#     sql_alchemy_conn = "postgresql+psycopg2://airflow_user:pass1234@localhost:5432/airflow_db"
#     engine = create_engine(sql_alchemy_conn)
#     try:
#         df.to_sql('bank_agency_reviews', con=engine, if_exists='append', index=False)
#         print("✅ Data successfully inserted into the database!")
#     except Exception as e:
#         print(f"⚠️ Error inserting data into the database: {e}")

# # Define the DAG
# with DAG('scrape_and_insert_bank_reviews', 
#          description='Scrape bank reviews and insert them into the DB',
#          schedule_interval=None, 
#          start_date=days_ago(1), 
#          catchup=False) as dag:

#     create_table_task = PythonOperator(
#         task_id='create_table_if_not_exists',
#         python_callable=create_table_if_not_exists,
#     )
    
#     extract_data_task = PythonOperator(
#         task_id='extract_data',
#         python_callable=extract_data,
#         provide_context=True,
#     )
    
#     insert_data_task = PythonOperator(
#         task_id='insert_data_into_db',
#         python_callable=insert_data_into_db,
#         provide_context=True,
#     )

#     # Task dependencies
#     create_table_task >> extract_data_task >> insert_data_task













# from airflow import DAG
# from airflow.operators.python_operator import PythonOperator
# from airflow.utils.dates import days_ago
# from sqlalchemy import create_engine
# from sqlalchemy.exc import SQLAlchemyError
# import time
# import pandas as pd
# from datetime import datetime
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import NoSuchElementException, TimeoutException
# from webdriver_manager.chrome import ChromeDriverManager

# # Path to ChromeDriver
# chrome_driver_path = ChromeDriverManager().install()

# # List of banks to scrape
# bank_urls = [
#     "https://www.google.com/maps/place/BANK+OF+AFRICA,+Agence+Abdelmoumen,+Casablanca./@33.5265726,-7.7316491,13z/data=!4m13!1m3!2m2!1sBMCE+Bank+of+Africa!6e2!3m8!1s0xda7d2b1401cddab:0xa09ec03c31179e50!8m2!3d33.5677444!4d-7.6264518!9m1!1b1!15sChNCTUNFIEJhbmsgb2YgQWZyaWNhkgEEYmFua-ABAA!16s%2Fg%2F1tklrxp2!5m1!1e1?entry=ttu&g_ep=EgoyMDI1MDMwNC4wIKXMDSoJLDEwMjExNDUzSAFQAw%3D%3D",
#     "https://www.google.com/maps/place/%D8%A8%D9%86%D9%83+%D8%A3%D9%81%D8%B1%D9%8A%D9%82%D9%8A%D8%A7%E2%80%AD/@33.5265726,-7.7316491,13z/data=!4m13!1m3!2m2!1sBMCE+Bank+of+Africa!6e2!3m8!1s0xda62cb2e1b355d9:0x92b1eb404df1b850!8m2!3d33.5563893!4d-7.6848036!9m1!1b1!15sChNCTUNFIEJhbmsgb2YgQWZyaWNhkgEEYmFua-ABAA!16s%2Fg%2F11crv4pc1x!5m1!1e1?entry=ttu&g_ep=EgoyMDI1MDMwNC4wIKXMDSoJLDEwMjExNDUzSAFQAw%3D%3D"
# ]

# # Function to initialize the WebDriver
# def initialize_driver():
#     options = Options()
#     options.add_argument("--headless")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     service = Service(chrome_driver_path)
#     driver = webdriver.Chrome(service=service, options=options)
#     return driver

# # Function to convert "X years ago" into a specific year
# def convert_relative_date(relative_date):
#     now = datetime.now()
#     try:
#         parts = relative_date.split()
#         if len(parts) >= 3:  # Handle years
#             if parts[3] == "un":
#                 parts[3] = "1"
#             years_ago = int(parts[3])
#             return str(now.year - years_ago)  # Calculate the year
#         elif "months" in relative_date:  # Handle months
#             return str(now.year)
#         elif "days" in relative_date:  # Handle days
#             return str(now.year)
#         else:
#             return "N/A"
#     except (IndexError, ValueError):
#         return "N/A"

# # Task to create the table if it doesn't exist
# def create_table_if_not_exists():
#     sql_alchemy_conn = "postgresql+psycopg2://airflow_user:pass1234@localhost:5432/airflow_db"
#     engine = create_engine(sql_alchemy_conn)
#     create_table_query = """
#     CREATE TABLE IF NOT EXISTS bank_agency_reviews (
#         id SERIAL PRIMARY KEY,
#         bank_name VARCHAR(255),
#         address TEXT,
#         review TEXT,
#         rating VARCHAR(10),
#         review_date VARCHAR(20)
#     );
#     """
#     try:
#         with engine.connect() as connection:
#             connection.execute(create_table_query)
#             print("✅ Table 'bank_agency_reviews' checked/created successfully.")
#     except SQLAlchemyError as e:
#         print(f"⚠️ Error creating table: {e}")

# # Task to extract data
# def extract_data(**kwargs):
#     driver = initialize_driver()  # Initialize WebDriver inside the task
#     all_data = []
#     for index, url in enumerate(bank_urls, start=1):
#         print(f"🔍 Scraping de l'URL {index}: {url}")
#         driver.get(url)
#         time.sleep(5)  # Laisser la page se charger

#         # 🔹 Extraire les avis et dates avant de cliquer sur "Présentation"
#         try:
#             review_elements = driver.find_elements(By.CSS_SELECTOR, "span.wiI7pd")
#             date_elements = driver.find_elements(By.CSS_SELECTOR, "span.rsqaWe")

#             print(f"🔍 Nombre d'avis trouvés : {len(review_elements)}")

#             # 🔹 Stocker temporairement les avis et dates
#             reviews = [review.text.strip() for review in review_elements]
#             dates = [convert_relative_date(date.text.strip()) for date in date_elements]

#         except Exception as e:
#             print(f"⚠️ Erreur lors de l'extraction des avis : {e}")
#             continue
        

#         # 🔹 Cliquer sur le div "Présentation" pour révéler l'adresse et le rating
#         try:
#             presentation_div = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "div.LRkQ2"))
#             )
#             presentation_div.click()
#             time.sleep(2)  # Attendre que l'adresse et le rating soient chargés
#         except TimeoutException:
#             print("⚠️ Impossible de cliquer sur le div de présentation")
#             continue

#         # 🔹 Récupérer le nom de la banque après avoir cliqué sur "Présentation"
#         try:
#             bank_name_element = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf.lfPIob"))
#             )
#             bank_name = bank_name_element.text.strip()
#         except TimeoutException:
#             bank_name = f"Banque {index}"

#         print(f"📌 Nom de la banque détecté : {bank_name}")

#         # 🔹 Récupérer l'adresse de la banque
#         try:
#             address_element = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "div.Io6YTe.fontBodyMedium.kR99db.fdkmkc"))
#             )
#             address = address_element.text.strip()
#         except TimeoutException:
#             address = "Non trouvée"

#         print(f"📌 Adresse de la banque détectée : {address}")

#         # 🔹 Récupérer le rating après avoir cliqué sur "Présentation"
#         try:
#             rating_element = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "div.F7nice span[aria-hidden='true']"))
#             )
#             rating = rating_element.text.strip()
#         except TimeoutException:
#             rating = "N/A"

#         print(f"📌 Note de la banque détectée : {rating}")

#         # 🔹 Stocker les données dans une liste

#         for i in range(len(reviews)):
#             try:
#                 all_data.append({
#                     "bank_name": bank_name,
#                     "address": address,
#                     "review": reviews[i],
#                     "rating": rating,  # Use the same rating for all reviews
#                     "review_date": dates[i] if i < len(dates) else "N/A"  # Only the year (e.g., 2020)
#                 })
#             except Exception as e:
#                 print(f"⚠️ Erreur lors du traitement d'un avis : {e}")
#     try:
#         driver.quit()  # Close the WebDriver after the task
#         driver.close()  # Close the WebDriver after the task
#     except Exception as e:
#         print(e)
#     kwargs['ti'].xcom_push(key='scraped_data', value=all_data)
#     return all_data 

# # Task to insert data into the database
# def insert_data_into_db(**kwargs):
#     ti = kwargs['ti']
#     scraped_data = ti.xcom_pull(task_ids='extract_data', key='scraped_data')
#     print("got data hhhhhhhhhhhhh", scraped_data)
#     if scraped_data:
#         df = pd.DataFrame(scraped_data)
#         sql_alchemy_conn = "postgresql+psycopg2://airflow_user:pass1234@localhost:5432/airflow_db"
#         engine = create_engine(sql_alchemy_conn)
#         try:
#             df.to_sql('bank_agency_reviews', con=engine, if_exists='append', index=False)
#             print("✅ Data successfully inserted into the database!")
#         except Exception as e:
#             print(f"⚠️ Error inserting data into the database: {e}")
#     else:
#         print("⚠️ No data to insert into the database.")

# # Define the DAG
# with DAG('scrape_and_insert_bank_reviews', 
#          description='Scrape bank reviews and insert them into the DB',
#          schedule_interval=None, 
#          start_date=days_ago(1), 
#          catchup=False) as dag:

#     create_table_task = PythonOperator(
#         task_id='create_table_if_not_exists',
#         python_callable=create_table_if_not_exists,
#     )
    
#     extract_data_task = PythonOperator(
#         task_id='extract_data',
#         python_callable=extract_data,
#         provide_context=True,
#     )
    
#     insert_data_task = PythonOperator(
#         task_id='insert_data_into_db',
#         python_callable=insert_data_into_db,
#         provide_context=True,
#     )

#     # Task dependencies
#     create_table_task >> extract_data_task >> insert_data_task








# from airflow import DAG
# from airflow.operators.python_operator import PythonOperator
# from airflow.utils.dates import days_ago
# from sqlalchemy import create_engine
# from sqlalchemy.exc import SQLAlchemyError
# import time
# import pandas as pd
# from datetime import datetime
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import NoSuchElementException, TimeoutException
# from webdriver_manager.chrome import ChromeDriverManager
# from sqlalchemy import text

# # Path to ChromeDriver
# chrome_driver_path = ChromeDriverManager().install()

# # List of banks to scrape
# # "https://www.google.com/maps/place/%D8%A8%D9%86%D9%83+%D8%A3%D9%81%D8%B1%D9%8A%D9%82%D9%8A%D8%A7%E2%80%AD/@33.5265726,-7.7316491,13z/data=!4m13!1m3!2m2!1sBMCE+Bank+of+Africa!6e2!3m8!1s0xda62cb2e1b355d9:0x92b1eb404df1b850!8m2!3d33.5563893!4d-7.6848036!9m1!1b1!15sChNCTUNFIEJhbmsgb2YgQWZyaWNhkgEEYmFua-ABAA!16s%2Fg%2F11crv4pc1x!5m1!1e1?entry=ttu&g_ep=EgoyMDI1MDMwNC4wIKXMDSoJLDEwMjExNDUzSAFQAw%3D%3D"
  
# bank_urls = [
#     "https://www.google.com/maps/place/BANK+OF+AFRICA,+Agence+Abdelmoumen,+Casablanca./@33.5265726,-7.7316491,13z/data=!4m13!1m3!2m2!1sBMCE+Bank+of+Africa!6e2!3m8!1s0xda7d2b1401cddab:0xa09ec03c31179e50!8m2!3d33.5677444!4d-7.6264518!9m1!1b1!15sChNCTUNFIEJhbmsgb2YgQWZyaWNhkgEEYmFua-ABAA!16s%2Fg%2F1tklrxp2!5m1!1e1?entry=ttu&g_ep=EgoyMDI1MDMwNC4wIKXMDSoJLDEwMjExNDUzSAFQAw%3D%3D",
#     "https://www.google.com/maps/place/BANK+OF+AFRICA,+Agence+Abdelmoumen,+Casablanca./@33.5265726,-7.7316491,13z/data=!4m13!1m3!2m2!1sBMCE+Bank+of+Africa!6e2!3m8!1s0xda7d2b1401cddab:0xa09ec03c31179e50!8m2!3d33.5677444!4d-7.6264518!9m1!1b1!15sChNCTUNFIEJhbmsgb2YgQWZyaWNhkgEEYmFua-ABAA!16s%2Fg%2F1tklrxp2!5m1!1e1?entry=ttu&g_ep=EgoyMDI1MDMwNC4wIKXMDSoJLDEwMjExNDUzSAFQAw%3D%3D",
# ]

# # Function to initialize the WebDriver
# def initialize_driver():
#     options = Options()
#     options.add_argument("--headless")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     service = Service(chrome_driver_path)
#     driver = webdriver.Chrome(service=service, options=options)
#     return driver

# # Function to convert "X years ago" into a specific year
# def convert_relative_date(relative_date):
#     now = datetime.now()
#     try:
#         parts = relative_date.split()
#         if len(parts) >= 3:  # Handle years
#             if parts[3] == "un":
#                 parts[3] = "1"
#             years_ago = int(parts[3])
#             return str(now.year - years_ago)  # Calculate the year
#         elif "months" in relative_date:  # Handle months
#             return str(now.year)
#         elif "days" in relative_date:  # Handle days
#             return str(now.year)
#         else:
#             return "N/A"
#     except (IndexError, ValueError):
#         return "N/A"

# # Task to create the table if it doesn't exist
# def create_table_if_not_exists():
#     sql_alchemy_conn = "postgresql+psycopg2://airflow_user:pass1234@localhost:5432/airflow_db"
#     engine = create_engine(sql_alchemy_conn)
#     create_table_query = """
#     CREATE TABLE IF NOT EXISTS bank_agency_reviews (
#         id SERIAL PRIMARY KEY,
#         bank_name VARCHAR(255),
#         branche_name VARCHAR(255),
#         address TEXT,
#         review TEXT,
#         rating VARCHAR(10),
#         review_date VARCHAR(20)
#     );
#     """
#     try:
#         with engine.connect() as connection:
#             connection.execute(create_table_query)
#             print("✅ Table 'bank_agency_reviews' checked/created successfully.")
#     except SQLAlchemyError as e:
#         print(f"⚠️ Error creating table: {e}")

# # Task to extract data
# def extract_data(**kwargs):
#     driver = initialize_driver()  # Initialize WebDriver inside the task
#     all_data = []
#     for index, url in enumerate(bank_urls, start=1):
#         print(f"🔍 Scraping de l'URL {index}: {url}")
#         driver.get(url)
#         time.sleep(5)  # Laisser la page se charger

#             # 🔹 Extraire les avis et dates avant de cliquer sur "Présentation"
#         try:
#             review_elements = driver.find_elements(By.CSS_SELECTOR, "span.wiI7pd")
#             date_elements = driver.find_elements(By.CSS_SELECTOR, "span.rsqaWe")
#             rating_elements = driver.find_elements(By.CSS_SELECTOR, "span.kvMYJc")  # Contient les étoiles

#             print(f"🔍 Nombre d'avis trouvés : {len(review_elements)}")

#             # 🔹 Stocker les avis, dates et notes
#             reviews = [review.text.strip() for review in review_elements]
#             dates = [convert_relative_date(date.text.strip()) for date in date_elements]

#             # 🔹 Extraction du nombre d'étoiles par avis
#             ratings = []
#             for rating_element in rating_elements:
#                 stars = rating_element.find_elements(By.CLASS_NAME, "elGi1d")  # Compter les étoiles pleines
#                 ratings.append(len(stars))

#         except Exception as e:
#             print(f"⚠️ Erreur lors de l'extraction des avis : {e}")
#             continue
        

#         # 🔹 Cliquer sur le div "Présentation" pour révéler l'adresse et le rating
#         try:
#             presentation_div = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "div.LRkQ2"))
#             )
#             presentation_div.click()
#             time.sleep(2)  # Attendre que l'adresse et le rating soient chargés
#         except TimeoutException:
#             print("⚠️ Impossible de cliquer sur le div de présentation")
#             continue

#         # 🔹 Récupérer le nom de la banque après avoir cliqué sur "Présentation"
#         try:
#             bank_name_element = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf.lfPIob"))
#             )
#             bank_name = bank_name_element.text.strip()
#         except TimeoutException:
#             bank_name = f"Banque {index}"

#         print(f"📌 Nom de la banque détecté : {bank_name}")

#         # 🔹 Récupérer l'adresse de la banque
#         try:
#             address_element = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "div.Io6YTe.fontBodyMedium.kR99db.fdkmkc"))
#             )
#             address = address_element.text.strip()
#         except TimeoutException:
#             address = "Non trouvée"

#         print(f"📌 Adresse de la banque détectée : {address}")

#         # 🔹 Récupérer le rating après avoir cliqué sur "Présentation"
#         try:
#             rating_element = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "div.F7nice span[aria-hidden='true']"))
#             )
#             rating = rating_element.text.strip()
#         except TimeoutException:
#             rating = "N/A"

#         print(f"📌 Note de la banque détectée : {rating}")

#         # 🔹 Stocker les données dans une liste

#         for i in range(len(reviews)):
#             try:
#                 all_data.append({
#                     "bank_name": bank_name,
#                     "branche_name": bank_name+" "+address,
#                     "address": address,
#                     "review": reviews[i],
#                     "rating": ratings[i] if i < len(ratings) else "N/A", # Use the same rating for all reviews
#                     "review_date": dates[i] if i < len(dates) else "N/A"  # Only the year (e.g., 2020)
#                 })
#             except Exception as e:
#                 print(f"⚠️ Erreur lors du traitement d'un avis : {e}")
#     try:
#         driver.quit()  # Close the WebDriver after the task
#         driver.close()  # Close the WebDriver after the task
#     except Exception as e:
#         print(e)
#     kwargs['ti'].xcom_push(key='scraped_data', value=all_data)
#     return all_data 

# # Task to insert data into the database

# def insert_data_into_db(**kwargs):
#     ti = kwargs['ti']
#     scraped_data = ti.xcom_pull(task_ids='extract_data', key='scraped_data')
#     print("got data hhhhhhhhhhhhh", scraped_data)
    
#     if scraped_data:
#         df = pd.DataFrame(scraped_data)
#         sql_alchemy_conn = "postgresql+psycopg2://airflow_user:pass1234@localhost:5432/airflow_db"
#         engine = create_engine(sql_alchemy_conn)
        
#         try:
#             # Iterate over each row in the DataFrame
#             for index, row in df.iterrows():
#                 # Normalize the review text to remove extra spaces and special characters
#                 normalized_review = " ".join(row['review'].split())  # Remove extra spaces
                
#                 # Check if the review already exists in the database using a parameterized query
#                 query = text("""
#                 SELECT 1 FROM bank_agency_reviews 
#                 WHERE bank_name = :bank_name 
#                 AND branche_name = :branche_name 
#                 AND review = :review 
#                 AND review_date = :review_date;
#                 """)
                
#                 # Execute the query with parameters
#                 result = engine.execute(query, {
#                     "bank_name": row['bank_name'],
#                     "branche_name": row['branche_name'],
#                     "review": normalized_review,  # Use the normalized review
#                     "review_date": row['review_date']
#                 }).fetchone()
                
#                 # If the review does not exist, insert it
#                 if not result:
#                     # Update the row with the normalized review
#                     row['review'] = normalized_review
#                     row.to_frame().T.to_sql('bank_agency_reviews', con=engine, if_exists='append', index=False)
#                     print(f"✅ Inserted review: {normalized_review}")
#                 else:
#                     print(f"⚠️ Review already exists: {normalized_review}")
            
#             print("✅ Data insertion process completed!")
#         except Exception as e:
#             print(f"⚠️ Error inserting data into the database: {e}")
#     else:
#         print("⚠️ No data to insert into the database.")

        
# # Define the DAG
# with DAG('scrape_and_insert_bank_reviews', 
#          description='Scrape bank reviews and insert them into the DB',
#          schedule_interval=None, 
#          start_date=days_ago(1), 
#          catchup=False) as dag:

#     create_table_task = PythonOperator(
#         task_id='create_table_if_not_exists',
#         python_callable=create_table_if_not_exists,
#     )
    
#     extract_data_task = PythonOperator(
#         task_id='extract_data',
#         python_callable=extract_data,
#         provide_context=True,
#     )
    
#     insert_data_task = PythonOperator(
#         task_id='insert_data_into_db',
#         python_callable=insert_data_into_db,
#         provide_context=True,
#     )

#     # Task dependencies
#     create_table_task >> extract_data_task >> insert_data_task


# from langdetect import detect
# from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
# from googletrans import Translator
# from sqlalchemy import create_engine, text
# from deep_translator import GoogleTranslator
# from airflow import DAG
# from airflow.operators.python_operator import PythonOperator
# from airflow.utils.dates import days_ago
# from sqlalchemy import create_engine
# from sqlalchemy.exc import SQLAlchemyError
# import time
# import pandas as pd
# from datetime import datetime
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import NoSuchElementException, TimeoutException
# from webdriver_manager.chrome import ChromeDriverManager
# from sqlalchemy import text


# # Import bank_urls from the external file
# # from bank_urls import bank_urls

#     # "https://www.google.com/maps/place/CIH+BANK/@33.9863553,-6.9484621,13z/data=!4m12!1m2!2m1!1scih+bank!3m8!1s0xda76d3ee69fbdcd:0x5890f67b66478786!8m2!3d33.9954991!4d-6.879399!9m1!1b1!15sCghjaWggYmFuayIDiAEBkgEEYmFua-ABAA!16s%2Fg%2F11b6hzvwbv!5m1!1e1?entry=ttu&g_ep=EgoyMDI1MDMwNC4wIKXMDSoASAFQAw%3D%3D",


# bank_urls = [
#     "https://www.google.com/maps/place/CIH+BANK/@33.9863553,-6.9484621,13z/data=!4m10!1m2!2m1!1scih+bank!3m6!1s0xda76c70de128e97:0x2f5cf53cfddf6dd4!8m2!3d33.999388!4d-6.8444769!15sCghjaWggYmFuayIDiAEBkgEEYmFua-ABAA!16s%2Fg%2F11hcjzjj66!5m1!1e1?entry=ttu&g_ep=EgoyMDI1MDMwNC4wIKXMDSoASAFQAw%3D%3D"
# ]

# # Path to ChromeDriver
# chrome_driver_path = ChromeDriverManager().install()

# # Function to initialize the WebDriver
# def initialize_driver():
#     options = Options()
#     options.add_argument("--headless")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     service = Service(chrome_driver_path)
#     driver = webdriver.Chrome(service=service, options=options)
#     return driver

# # Function to convert "X years ago" into a specific year
# def convert_relative_date(relative_date):
#     now = datetime.now()
#     try:
#         parts = relative_date.split()
#         if len(parts) >= 3:  # Handle years
#             if parts[3] == "un":
#                 parts[3] = "1"
#             years_ago = int(parts[3])
#             return str(now.year - years_ago)  # Calculate the year
#         elif "months" in relative_date:  # Handle months
#             return str(now.year)
#         elif "days" in relative_date:  # Handle days
#             return str(now.year)
#         else:
#             return "N/A"
#     except (IndexError, ValueError):
#         return "N/A"

# # Task to create the table if it doesn't exist
# def create_table_if_not_exists():
#     sql_alchemy_conn = "postgresql+psycopg2://airflow_user:pass1234@localhost:5432/airflow_db"
#     engine = create_engine(sql_alchemy_conn)
#     create_table_query = """
#     CREATE TABLE IF NOT EXISTS bank_agency_reviews (
#         id SERIAL PRIMARY KEY,
#         bank_name VARCHAR(255),
#         branche_name VARCHAR(255),
#         address TEXT,
#         review TEXT,
#         rating VARCHAR(10),
#         review_date VARCHAR(20),
#         language varchar(20),
#         review_sentiment varchar(20)
#     );
#     """
#     try:
#         with engine.connect() as connection:
#             connection.execute(create_table_query)
#             print("✅ Table 'bank_agency_reviews' checked/created successfully.")
#     except SQLAlchemyError as e:
#         print(f"⚠️ Error creating table: {e}")

# # Task to extract data
# def extract_data(**kwargs):
#     driver = initialize_driver()  # Initialize WebDriver inside the task
#     all_data = []
#     for index, url in enumerate(bank_urls, start=1):
#         print(f"🔍 Scraping de l'URL {index}: {url}")
#         driver.get(url)
#         time.sleep(5)  # Laisser la page se charger

#         # 🔹 Extraire les avis et dates avant de cliquer sur "Présentation"
#         try:
#             review_elements = driver.find_elements(By.CSS_SELECTOR, "span.wiI7pd")
#             date_elements = driver.find_elements(By.CSS_SELECTOR, "span.rsqaWe")
#             rating_elements = driver.find_elements(By.CSS_SELECTOR, "span.kvMYJc")  # Contient les étoiles

#             print(f"🔍 Nombre d'avis trouvés : {len(review_elements)}")

#             # 🔹 Stocker les avis, dates et notes
#             reviews = [review.text.strip() for review in review_elements]
#             dates = [convert_relative_date(date.text.strip()) for date in date_elements]

#             # 🔹 Extraction du nombre d'étoiles par avis
#             ratings = []
#             for rating_element in rating_elements:
#                 stars = rating_element.find_elements(By.CLASS_NAME, "elGi1d")  # Compter les étoiles pleines
#                 ratings.append(len(stars))

#         except Exception as e:
#             print(f"⚠️ Erreur lors de l'extraction des avis : {e}")
#             continue

#         # 🔹 Cliquer sur le div "Présentation" pour révéler l'adresse et le rating
#         try:
#             presentation_div = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "div.LRkQ2"))
#             )
#             presentation_div.click()
#             time.sleep(2)  # Attendre que l'adresse et le rating soient chargés
#         except TimeoutException:
#             print("⚠️ Impossible de cliquer sur le div de présentation")
#             continue

#         # 🔹 Récupérer le nom de la banque après avoir cliqué sur "Présentation"
#         try:
#             bank_name_element = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf.lfPIob"))
#             )
#             bank_name = bank_name_element.text.strip()
#         except TimeoutException:
#             bank_name = f"Banque {index}"

#         print(f"📌 Nom de la banque détecté : {bank_name}")

#         # 🔹 Récupérer l'adresse de la banque
#         try:
#             address_element = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "div.Io6YTe.fontBodyMedium.kR99db.fdkmkc"))
#             )
#             address = address_element.text.strip()
#         except TimeoutException:
#             address = "Non trouvée"

#         print(f"📌 Adresse de la banque détectée : {address}")

#         # 🔹 Récupérer le rating après avoir cliqué sur "Présentation"
#         try:
#             rating_element = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "div.F7nice span[aria-hidden='true']"))
#             )
#             rating = rating_element.text.strip()
#         except TimeoutException:
#             rating = "N/A"

#         print(f"📌 Note de la banque détectée : {rating}")

#         # 🔹 Stocker les données dans une liste
#         for i in range(len(reviews)):
#             try:
#                 all_data.append({
#                     "bank_name": bank_name,
#                     "branche_name": bank_name + " " + address,
#                     "address": address,
#                     "review": reviews[i],
#                     "rating": ratings[i] if i < len(ratings) else "N/A",  # Use the same rating for all reviews
#                     "review_date": dates[i] if i < len(dates) else "N/A"  # Only the year (e.g., 2020)
#                 })
#             except Exception as e:
#                 print(f"⚠️ Erreur lors du traitement d'un avis : {e}")
#     try:
#         driver.quit()  # Close the WebDriver after the task
#         driver.close()  # Close the WebDriver after the task
#     except Exception as e:
#         print(e)
#     kwargs['ti'].xcom_push(key='scraped_data', value=all_data)
#     return all_data

# # Task to insert data into the database
# def translate_text(text, source_lang='auto', target_lang='en'):
#     """
#     Translate text using Google Translate API.
#     """
#     translator = Translator()
#     try:
#         translated = translator.translate(text, src=source_lang, dest=target_lang)
#         return translated.text
#     except Exception as e:
#         print(f"⚠️ Translation failed for text: {text}. Error: {e}")
#         return text  # Fallback to the original text if translation fails
# from deep_translator import GoogleTranslator  # Import the translation library
# from deep_translator import GoogleTranslator  # Import the translation library

# def translate_text(text, source_lang='auto', target_lang='en'):
#     """
#     Helper function to translate text from a source language to a target language.
#     """
#     try:
#         translated_text = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
#         print(f"🌐 Original: {text}")
#         print(f"🌐 Translated: {translated_text}")
#         return translated_text
#     except Exception as e:
#         print(f"⚠️ Error translating text: {e}")
#         return text  # Fallback to the original text if translation fails

# def get_sentiment(review):
#     from transformers import pipeline
#     sentiment_pipeline = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
#     result = sentiment_pipeline(review)[0]
#     label = result['label']
#     if "5" in label or "4" in label:
#         sentiment = "Positive"
#     elif "3" in label:
#         sentiment = "Neutral"
#     else:
#         sentiment = "Negative"
#     return sentiment


# def detect_language(text):
#     try:
#         return detect(text)
#     except Exception as e:
#         print(f"⚠️ Erreur lors de la détection de la langue: {e}")
#         return "unknown"  # Retourner "unknown" en cas d'erreur


# def insert_data_into_db(**kwargs):
#     ti = kwargs['ti']
#     scraped_data = ti.xcom_pull(task_ids='extract_data', key='scraped_data')
#     print("got data hhhhhhhhhhhhh", scraped_data)
    
#     if scraped_data:
#         df = pd.DataFrame(scraped_data)
#         sql_alchemy_conn = "postgresql+psycopg2://airflow_user:pass1234@localhost:5432/airflow_db"
#         engine = create_engine(sql_alchemy_conn)
        
#         try:
#             # Iterate over each row in the DataFrame
#             for index, row in df.iterrows():
#                 # Translate all fields
#                 translated_bank_name = translate_text(row['bank_name'])
#                 translated_branche_name = translate_text(row['branche_name'])
#                 translated_review = translate_text(row['review'])
#                 translated_address = translate_text(row['address'])
                
                

#                 # Normalize the translated review text to remove extra spaces
#                 normalized_review = " ".join(translated_review.split())
#                 lang = detect(normalized_review)
#                 review_sentiment = get_sentiment(normalized_review)
#                 # Check if the review already exists in the database using a parameterized query
#                 query = text("""
#                 SELECT 1 FROM bank_agency_reviews 
#                 WHERE bank_name = :bank_name 
#                 AND branche_name = :branche_name 
#                 AND review = :review 
#                 AND review_date = :review_date;
#                 """)
                
#                 # Execute the query with parameters
#                 result = engine.execute(query, {
#                     "bank_name": translated_bank_name,
#                     "branche_name": translated_branche_name,
#                     "review": normalized_review,
#                     "review_date": row['review_date'],
#                     "language" : lang
#                 }).fetchone()
                
#                 # If the review does not exist, insert it
#                 if not result:
#                     # Update the row with the translated fields
#                     row['bank_name'] = translated_bank_name
#                     row['branche_name'] = translated_branche_name
#                     row['review'] = normalized_review
#                     row['address'] = translated_address
#                     row['language'] = lang
#                     row['review_sentiment'] = review_sentiment
#                     # Insert the row into the database
#                     row.to_frame().T.to_sql('bank_agency_reviews', con=engine, if_exists='append', index=False)
#                     print(f"✅ Inserted review: {normalized_review}")
#                 else:
#                     print(f"⚠️ Review already exists: {normalized_review}")
            
#             print("✅ Data insertion process completed!")
#         except Exception as e:
#             print(f"⚠️ Error inserting data into the database: {e}")
#     else:
#         print("⚠️ No data to insert into the database.")


# # Define the DAG
# with DAG('scrape_and_insert_bank_reviews', 
#          description='Scrape bank reviews and insert them into the DB',
#          schedule_interval=None, 
#          start_date=days_ago(1), 
#          catchup=False) as dag:

#     create_table_task = PythonOperator(
#         task_id='create_table_if_not_exists',
#         python_callable=create_table_if_not_exists,
#     )
    
#     extract_data_task = PythonOperator(
#         task_id='extract_data',
#         python_callable=extract_data,
#         provide_context=True,
#     )
    
#     insert_data_task = PythonOperator(
#         task_id='insert_data_into_db',
#         python_callable=insert_data_into_db,
#         provide_context=True,
#     )

#     # Task dependencies
#     create_table_task >> extract_data_task >> insert_data_task





# extract data--------------------------------------------

def extract_data(**kwargs):
    scroll_distance = 2000  # Scroll distance in pixels
    max_scrolls = 5  # Increase scroll attempts to load more data
    scroll_count = 0
    all_links = set()  # Store all unique links
    retry_count = 0
    
    driver = initialize_driver()  # Initialize WebDriver inside the task
    driver.get("https://www.google.com/maps/search/attijari/@33.9867338,-7.0102649,11934m/data=!3m2!1e3!4b1!5m1!1e1?entry=ttu&g_ep=EgoyMDI1MDMxMi4wIKXMDSoASAFQAw%3D%3D")
    all_data = []
    
    def extract_links():
        elements = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
        return {el.get_attribute("href") for el in elements if el.get_attribute("href")}
    
    while scroll_count < max_scrolls:
        current_links = extract_links()
        all_links.update(current_links)  # Add new links to the set

        print(f"Scroll {scroll_count + 1}: Found {len(current_links)} links.")
        
        # Scroll down to load more elements
        try:
            scrollable_element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd"))
            )
            driver.execute_script("arguments[0].scrollTop += arguments[0].scrollHeight", scrollable_element)
            time.sleep(3)
        except Exception as e:
            print(f"⚠️ Erreur lors du scrolling : {e}")

        # Wait for new links to load
        try:
            WebDriverWait(driver,5).until(
                lambda d: len(extract_links()) > len(current_links)
            )
        except Exception:
            print("⚠️ No new links loaded after scrolling. Retrying...")
            retry_count += 1
            if retry_count > 3:
                break  # Stop retrying if too many failures
            time.sleep(3)

        scroll_count += 1
    
    for index, url in enumerate(all_links, start=1):
        print(f"🔍 Scraping de l'URL {index}: {url}")
        driver.get(url)
        time.sleep(2)  # Laisser la page se charger

        

      
        
    #    ------------
        try:
            bank_name = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf.lfPIob"))
            ).text.strip()
        except:
            bank_name = f"Banque {index}"
        
        try:
            address = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.Io6YTe.fontBodyMedium.kR99db.fdkmkc"))
            ).text.strip()
        except:
            address = "Non trouvée"
        
       
        
        # click on div review to access to review reviews

        try:
            review_div = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.Gpq6kf"))
            )
            review_div.click()
            time.sleep(5)
        except:
            print("⚠️ Impossible de cliquer sur 'reviews'")
        
        try:
            WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde"))
            )
        except Exception as e:
            print("Timed out waiting for reviews section to load.")
            driver.quit()
            exit()
        
        def extract_reviews():
            reviews = driver.find_elements(By.CSS_SELECTOR, "div.MyEned span.wiI7pd")
            return [review.text for review in reviews]
        
        scroll_distance = 2000  # Scroll distance in pixels
        max_scrolls = 10  # Maximum number of scroll attempts
        scroll_count = 0
        all_reviews = set()  # Use a set to store unique reviews
        retry_count = 0

        while scroll_count < max_scrolls:
            # Extract reviews in the current view
            current_reviews = extract_reviews()
            unique_reviews = set(current_reviews) - all_reviews  # Get only new reviews
            all_reviews.update(unique_reviews)  # Add new reviews to the set

            print(f"Scroll {scroll_count + 1}: Found {len(unique_reviews)} new reviews.")

            # Scroll down by the fixed distance
            try:
                scrollable_element = driver.find_element(By.CSS_SELECTOR, "div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde")
                driver.execute_script(f"arguments[0].scrollTop += {scroll_distance}", scrollable_element)
                time.sleep(3)  # Allow time for new reviews to load
            except Exception as e:
                print(f"⚠️ Error during scrolling: {e}")

            # Wait for new reviews to load
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: len(extract_reviews()) > len(current_reviews)
                )
            except Exception:
                print("⚠️ No new reviews loaded after scrolling. Retrying...")
                retry_count += 1
                if retry_count > 3:
                    break  # Stop retrying if too many failures
                time.sleep(5)
            scroll_count += 1

        reviews = list(all_reviews)

        try:
            date_elements = driver.find_elements(By.CSS_SELECTOR, "span.rsqaWe")
            rating_elements = driver.find_elements(By.CSS_SELECTOR, "span.kvMYJc")

            dates = [convert_relative_date(date.text.strip()) for date in date_elements]
            ratings = [len(r.find_elements(By.CLASS_NAME, "elGi1d")) for r in rating_elements]
        except Exception as e:
            print(f"⚠️ Erreur lors de l'extraction des avis : {e}")
            continue

        
        for i in range(len(reviews)):
            try:
                all_data.append({
                    "bank_name": bank_name,
                    "branche_name": f"{bank_name} {address}",
                    "address": address,
                    "review": reviews[i],
                    "rating": ratings[i] if i < len(ratings) else "N/A",
                    "review_date": dates[i] if i < len(dates) else "N/A"
                })
            except Exception as e:
                print(f"⚠️ Erreur lors du stockage des données : {e}")
    
    try:
        driver.quit()
    except Exception as e:
        print(f"⚠️ Erreur lors de la fermeture du WebDriver: {e}")
    finally :
        driver.quit()
    kwargs['ti'].xcom_push(key='scraped_data', value=all_data)
    return all_data






# # here is the zombir






# from airflow import DAG
# from airflow.operators.python_operator import PythonOperator
# from airflow.utils.dates import days_ago
# from sqlalchemy import create_engine, text
# from sqlalchemy.exc import SQLAlchemyError
# import time
# import pandas as pd
# from datetime import datetime
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import NoSuchElementException, TimeoutException
# from webdriver_manager.chrome import ChromeDriverManager
# from deep_translator import GoogleTranslator
# from langdetect import detect
# from datetime import timedelta

# # Define bank URLs
# # bank_urls = [
# #     "https://www.google.com/maps/place/CIH+BANK/@33.9863553,-6.9484621,13z/data=!4m10!1m2!2m1!1scih+bank!3m6!1s0xda76c70de128e97:0x2f5cf53cfddf6dd4!8m2!3d33.999388!4d-6.8444769!15sCghjaWggYmFuayIDiAEBkgEEYmFua-ABAA!16s%2Fg%2F11hcjzjj66!5m1!1e1?entry=ttu&g_ep=EgoyMDI1MDMwNC4wIKXMDSoASAFQAw%3D%3D",
# #     "https://www.google.com/maps/place/CIH+BANK/@33.9863553,-6.9484621,13z/data=!4m12!1m2!2m1!1scih+bank!3m8!1s0xda76d24964dd881:0xae1c4ec6c91e3837!8m2!3d33.9760898!4d-6.8874566!9m1!1b1!15sCghjaWggYmFuayIDiAEBkgEEYmFua-ABAA!16s%2Fg%2F11b6jg_p7d!5m1!1e1?entry=ttu&g_ep=EgoyMDI1MDMwNC4wIKXMDSoASAFQAw%3D%3D"
# # ]

# # Function to initialize the WebDriver
# def initialize_driver():
#     options = Options()
#     options.add_argument("--headless")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     chrome_driver_path = ChromeDriverManager().install()
#     service = Service(chrome_driver_path)
#     driver = webdriver.Chrome(service=service, options=options)
#     return driver

# # Function to convert "X years ago" into a specific year
# def convert_relative_date(relative_date):
#     now = datetime.now()
#     try:
#         parts = relative_date.split()
#         if len(parts) >= 3:  # Handle years
#             if parts[3] == "un":
#                 parts[3] = "1"
#             years_ago = int(parts[3])
#             return str(now.year - years_ago)  # Calculate the year
#         elif "months" in relative_date:  # Handle months
#             return str(now.year)
#         elif "days" in relative_date:  # Handle days
#             return str(now.year)
#         else:
#             return "N/A"
#     except (IndexError, ValueError):
#         return "N/A"

# # Task to create the table if it doesn't exist
# def create_table_if_not_exists():
#     sql_alchemy_conn = "postgresql+psycopg2://airflow_user:pass1234@localhost:5432/airflow_db"
#     engine = create_engine(sql_alchemy_conn)
#     create_table_query = """
#     CREATE TABLE IF NOT EXISTS bank_agency_reviews (
#         id SERIAL PRIMARY KEY,
#         bank_name VARCHAR(255),
#         branche_name VARCHAR(255),
#         address TEXT,
#         review TEXT,
#         rating VARCHAR(10),
#         review_date VARCHAR(20),
#         language varchar(20),
#         review_sentiment varchar(20)
#     );
#     """
#     try:
#         with engine.connect() as connection:
#             connection.execute(create_table_query)
#             print("✅ Table 'bank_agency_reviews' checked/created successfully.")
#     except SQLAlchemyError as e:
#         print(f"⚠️ Error creating table: {e}")



# def extract_links(**kwargs):
#     driver = initialize_driver()
#     all_links = set()

#     try:
#         driver.get("https://www.google.com/maps/search/attijari/@33.9867338,-7.0102649,11934m/data=!3m2!1e3!4b1!5m1!1e1?entry=ttu&g_ep=EgoyMDI1MDMxMi4wIKXMDSoASAFQAw%3D%3D")
        
#         def get_links():
#             elements = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
#             return {el.get_attribute("href") for el in elements if el.get_attribute("href")}

#         for _ in range(5):  # Scroll 5 times
#             all_links.update(get_links())
#             scrollable_element = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd"))
#             )
#             driver.execute_script("arguments[0].scrollTop += arguments[0].scrollHeight", scrollable_element)
#             time.sleep(5)

#     except Exception as e:
#         print(f"⚠️ Error extracting links: {e}")
#     finally:
#         driver.quit()

#     kwargs['ti'].xcom_push(key='extracted_links', value=list(all_links))
#     print(f"✅ Extracted {len(all_links)} links.")
#     return list(all_links)


# def extract_data(**kwargs):
#     links = kwargs['ti'].xcom_pull(task_ids='extract_links', key='extracted_links')
#     if not links:
#         print("⚠️ No links found, skipping data extraction.")
#         return []

#     all_data = []  # Store all scraped data

#     # Initialize WebDriver
#     driver = initialize_driver()

#     try:
#         # Scrape data from each link
#         for index, url in enumerate(links, start=1):
#             print(f"🔍 Scraping URL {index}: {url}")
#             driver.get(url)
#             time.sleep(5)  # Let the page load

#             # Extract bank name and address
#             try:
#                 bank_name = WebDriverWait(driver, 10).until(
#                     EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf.lfPIob"))
#                 ).text.strip()
#             except Exception:
#                 bank_name = f"Banque {index}"

#             try:
#                 address = WebDriverWait(driver, 10).until(
#                     EC.presence_of_element_located((By.CSS_SELECTOR, "div.Io6YTe.fontBodyMedium.kR99db.fdkmkc"))
#                 ).text.strip()
#             except Exception:
#                 address = "Non trouvée"

#             # Click on the reviews section
#             try:
#                 review_div = WebDriverWait(driver, 10).until(
#                     EC.presence_of_element_located((By.CSS_SELECTOR, "div.Gpq6kf"))
#                 )
#                 review_div.click()
#                 time.sleep(5)  # Wait for reviews to load
#             except Exception:
#                 print("⚠️ Impossible de cliquer sur 'reviews'")
#                 continue  # Skip this URL if reviews section cannot be clicked

#             # Wait for reviews section to load
#             try:
#                 WebDriverWait(driver, 10).until(
#                     EC.presence_of_element_located((By.CSS_SELECTOR, "div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde"))
#                 )
#             except Exception as e:
#                 print("Timed out waiting for reviews section to load.")
#                 continue  # Skip this URL if reviews section does not load

#             # Extract reviews
#             reviews = [review.text for review in driver.find_elements(By.CSS_SELECTOR, "div.MyEned span.wiI7pd")]

#             # Extract dates and ratings
#             try:
#                 date_elements = driver.find_elements(By.CSS_SELECTOR, "span.rsqaWe")
#                 rating_elements = driver.find_elements(By.CSS_SELECTOR, "span.kvMYJc")

#                 dates = [convert_relative_date(date.text.strip()) for date in date_elements]
#                 ratings = [len(r.find_elements(By.CLASS_NAME, "elGi1d")) for r in rating_elements]
#             except Exception as e:
#                 print(f"⚠️ Error extracting dates and ratings: {e}")
#                 continue  # Skip this URL if dates/ratings cannot be extracted

#             # Store data
#             for i in range(len(reviews)):
#                 try:
#                     all_data.append({
#                         "bank_name": bank_name,
#                         "branche_name": f"{bank_name} {address}",
#                         "address": address,
#                         "review": reviews[i],
#                         "rating": ratings[i] if i < len(ratings) else "N/A",
#                         "review_date": dates[i] if i < len(dates) else "N/A"
#                     })
#                 except Exception as e:
#                     print(f"⚠️ Error storing data: {e}")

#     except Exception as e:
#         print(f"⚠️ Error during scraping: {e}")
#     finally:
#         # Ensure the WebDriver is closed
#         try:
#             driver.quit()
#             print("WebDriver closed.")
#         except Exception as e:
#             print(f"⚠️ Error closing WebDriver: {e}")

#     # Push data to XCom for downstream tasks
#     kwargs['ti'].xcom_push(key='scraped_data', value=all_data)
#     return all_data

# def translate_text(text, source_lang='auto', target_lang='en'):
#     """
#     Helper function to translate text from a source language to a target language.
#     If the text is in French, it will not be translated.
#     """
#     try:
#         # Detect language
#         detected_lang = detect(text)
        
#         # Skip translation if the text is in French
#         if detected_lang == 'fr':
#             print(f"🛑 Skipping translation (French detected): {text}")
#             return text
        
#         # Translate if it's not in French
#         translated_text = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
#         print(f"🌐 Original: {text}")
#         print(f"🌐 Translated: {translated_text}")
#         return translated_text
#     except Exception as e:
#         print(f"⚠️ Error translating text: {e}")
#         return text  # Fallback to the original text if translation fails


# def get_sentiment(review):
#     from transformers import pipeline
#     sentiment_pipeline = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
#     result = sentiment_pipeline(review)[0]
#     label = result['label']
#     if "5" in label or "4" in label:
#         sentiment = "Positive"
#     elif "3" in label :
#         sentiment = "Neutral"
#     else:
#         sentiment = "Negative"
#     return sentiment

# def detect_language(text):
#     try:
#         return detect(text)
#     except Exception as e:
#         print(f"⚠️ Erreur lors de la détection de la langue: {e}")
#         return "unknown"  # Retourner "unknown" en cas d'erreur

# def insert_data_into_db(**kwargs):
#     ti = kwargs['ti']
#     scraped_data = ti.xcom_pull(task_ids='extract_data', key='scraped_data')
#     print("got data hhhhhhhhhhhhh", scraped_data)
    
#     if scraped_data:
#         df = pd.DataFrame(scraped_data)
#         sql_alchemy_conn = "postgresql+psycopg2://airflow_user:pass1234@localhost:5432/airflow_db"
#         engine = create_engine(sql_alchemy_conn)
        
#         try:
#             # Iterate over each row in the DataFrame
#             for index, row in df.iterrows():
#                 # Translate all fields
#                 translated_bank_name = translate_text(row['bank_name'])
#                 translated_branche_name = translate_text(row['branche_name'])
#                 translated_review = translate_text(row['review'])
#                 translated_address = translate_text(row['address'])
                
#                 # Normalize the translated review text to remove extra spaces
#                 normalized_review = " ".join(translated_review.split())
#                 lang = detect(normalized_review)
#                 review_sentiment = get_sentiment(normalized_review)
                
#                 # Check if the review already exists in the database using a parameterized query
#                 query = text("""
#                 SELECT 1 FROM bank_agency_reviews 
#                 WHERE bank_name = :bank_name 
#                 AND branche_name = :branche_name 
#                 AND review = :review 
#                 AND review_date = :review_date;
#                 """)
                
#                 # Execute the query with parameters
#                 result = engine.execute(query, {
#                     "bank_name": translated_bank_name,
#                     "branche_name": translated_branche_name,
#                     "review": normalized_review,
#                     "review_date": row['review_date'],
#                     "language": lang
#                 }).fetchone()
                
#                 # If the review does not exist, insert it
#                 if not result:
#                     # Update the row with the translated fields
#                     row['bank_name'] = translated_bank_name
#                     row['branche_name'] = translated_branche_name
#                     row['review'] = normalized_review
#                     row['address'] = translated_address
#                     row['language'] = lang
#                     row['review_sentiment'] = review_sentiment
#                     # Insert the row into the database
#                     row.to_frame().T.to_sql('bank_agency_reviews', con=engine, if_exists='append', index=False)
#                     print(f"✅ Inserted review: {normalized_review}")
#                 else:
#                     print(f"⚠️ Review already exists: {normalized_review}")
            
#             print("✅ Data insertion process completed!")
#         except Exception as e:
#             print(f"⚠️ Error inserting data into the database: {e}")
#     else:
#         print("⚠️ No data to insert into the database.")

# # Define the DAG
# with DAG('scrape_and_insert_bank_reviews', 
#          description='Scrape bank reviews and insert them into the DB',
#          schedule_interval=None, 
#          start_date=days_ago(1), 
#          catchup=False) as dag:

#     create_table_task = PythonOperator(
#         task_id='create_table_if_not_exists',
#         python_callable=create_table_if_not_exists,
#     )

#     task_extract_links = PythonOperator(
#         task_id='extract_links',
#         python_callable=extract_links,
#         provide_context=True,
#         execution_timeout=timedelta(minutes=60)
#     )
    
#     extract_data_task = PythonOperator(
#         task_id='extract_data',
#         python_callable=extract_data,
#         provide_context=True,
#         execution_timeout=timedelta(minutes=360)
#     )
    
#     insert_data_task = PythonOperator(
#         task_id='insert_data_into_db',
#         python_callable=insert_data_into_db,
#         provide_context=True,
#     )

#     # Task dependencies
#     create_table_task >> task_extract_links >> extract_data_task >> insert_data_task

