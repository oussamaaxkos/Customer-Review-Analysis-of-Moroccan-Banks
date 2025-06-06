from langdetect import detect
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from googletrans import Translator
from sqlalchemy import create_engine, text
from deep_translator import GoogleTranslator
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import time
import pandas as pd
from datetime import datetime , timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from sqlalchemy import text
import re


from airflow.operators.bash import BashOperator
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation


import pandas as pd
from sqlalchemy import create_engine


# Import bank_urls from the external file
# from bank_urls import bank_urls

bank_urls = [
    "https://www.google.com/maps/place/CIH/@33.999388,-6.9165747,15397m/data=!3m1!1e3!4m10!1m2!2m1!1scih+bank!3m6!1s0xda76ce1ba996839:0xea0bce250e2160a2!8m2!3d33.9863553!4d-6.8763643!15sCghjaWggYmFuayIDiAEBkgEEYmFua-ABAA!16s%2Fg%2F1q5bxc5q5!5m1!1e1?entry=ttu&g_ep=EgoyMDI1MDMxMi4wIKXMDSoASAFQAw%3D%3D"
]


# "https://www.google.com/maps/place/CIH+BANK/@33.9863553,-6.9484621,13z/data=!4m12!1m2!2m1!1scih+bank!3m8!1s0xda76d3ee69fbdcd:0x5890f67b66478786!8m2!3d33.9954991!4d-6.879399!9m1!1b1!15sCghjaWggYmFuayIDiAEBkgEEYmFua-ABAA!16s%2Fg%2F11b6hzvwbv!5m1!1e1?entry=ttu&g_ep=EgoyMDI1MDMwNC4wIKXMDSoASAFQAw%3D%3D",




# Path to ChromeDriver
chrome_driver_path = ChromeDriverManager().install()

# Function to initialize the WebDriver
def initialize_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Function to convert "X years ago" into a specific year
def convert_relative_date(relative_date):
    now = datetime.now()
    try:
        parts = relative_date.split()
        if len(parts) >= 3:  # Handle years
            if parts[3] == "un":
                parts[3] = "1"
            years_ago = int(parts[3])
            return str(now.year - years_ago)  # Calculate the year
        elif "months" in relative_date:  # Handle months
            return str(now.year)
        elif "days" in relative_date:  # Handle days
            return str(now.year)
        else:
            return "N/A"
    except (IndexError, ValueError):
        return "N/A"

# Task to create the table if it doesn't exist
def create_table_if_not_exists():
    sql_alchemy_conn = "postgresql+psycopg2://airflow_user:pass1234@localhost:5432/airflow_db"
    engine = create_engine(sql_alchemy_conn)
    create_table_query = """
    CREATE TABLE IF NOT EXISTS bank_agency_reviews (
        id SERIAL PRIMARY KEY,
        bank_name VARCHAR(255), 
        branche_name VARCHAR(255),
        address TEXT,
        review TEXT, 
        rating VARCHAR(10),
        review_date VARCHAR(20), 
        scrapping_date varchar(100) 
    );
    """                
                    # row['language'] = lang
                    # row['review_sentiment'] = review_sentiment
                    
                    


    try:
        with engine.connect() as connection:
            connection.execute(create_table_query)
            print("✅ Table 'bank_agency_reviews' checked/created successfully.")
    except SQLAlchemyError as e:
        print(f"⚠️ Error creating table: {e}")



def extract_links(**kwargs):
    driver = initialize_driver()
    # List of search result URLs to scrape


    morocco_cities = [
    "Casablanca"
    ]

    moroccan_banks = [
    "Attijariwafa+Bank"
    ]

    cities = [
    "Casablanca"
    ]

    # Latitudes et longitudes correspondantes (à garder coordonnées correctes)
    latitudes = [
        "33.5731104"
    ]

    longitudes = [
    "-7.5898434"
    ]



    # Génération des URLs de recherche Google Maps
    def generate_search_urls():
        search_urls = []
        for bank in moroccan_banks:
            for city, lat, long in zip(cities, latitudes, longitudes):
                url = f'https://www.google.com/maps/search/{bank}+{city}/@{lat},{long},14059m/data=!3m2!1e3!4b1!5m1!1e1?entry=ttu'
                search_urls.append(url)
                print(url)
        return search_urls
    


    def extract_links(driver, search_urls):
        all_links = {}

        def extract():
            elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/place/']")
            return {el.get_attribute("href") for el in elements if el.get_attribute("href")}

        for url in search_urls:
            driver.get(url)
            time.sleep(3)
            scroll_count = 0
            max_scrolls = 3  # Suggestion : augmenter à 5 si tu veux récupérer plus de résultats
            links_in_page = set()

            while scroll_count < max_scrolls:
                current_links = extract()
                links_in_page.update(current_links)
                print(f"Page {url} | Scroll {scroll_count + 1}: Found {len(current_links)} links.")

                try:
                    scrollable_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
                    )
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_element)
                    time.sleep(3)
                except Exception as e:
                    print(f"Error scrolling: {e}")
                    break

                scroll_count += 1

            all_links[url] = list(links_in_page)

        return all_links




    search_urls = []
    for bankname in moroccan_banks:
        for city in morocco_cities:
            link = f'https://www.google.com/maps/search/{bankname}+{city}/@31.6237775,-8.0611631,14059m/data=!3m2!1e3!4b1!5m1!1e1?entry=ttu&g_ep=EgoyMDI1MDUwNy4wIKXMDSoASAFQAw%3D%3D'
            search_urls.append(link)
            print(link);

    
    all_links = {}  # Dictionary to store {search_url: [list_of_links]}
    def extract():
        elements = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
        return {el.get_attribute("href") for el in elements if el.get_attribute("href")}
    
    for url in search_urls:
        driver.get(url)
        time.sleep(3)  # Let the page load

        scroll_distance = 2000
        max_scrolls = 5
        scroll_count = 0
        retry_count = 0

        all_links[url] = set()

        while scroll_count < max_scrolls:
            current_links = extract()
            all_links[url].update(current_links)
            print(f"🔄 Page: {url} | Scroll {scroll_count + 1}: Found {len(current_links)} links.")

            try:
                scrollable_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd"))
                )
                driver.execute_script("arguments[0].scrollTop += arguments[0].scrollHeight", scrollable_element)
                time.sleep(3)
            except Exception as e:
                print(f"⚠️ Scrolling Error: {e}")

            try:
                WebDriverWait(driver, 10).until(
                    lambda d: len(extract()) > len(current_links)
                )
            except Exception:
                print("⚠️ No new links loaded after scrolling. Retrying...")
                retry_count += 1
                if retry_count > 3:
                    break
                time.sleep(5)

            scroll_count += 1

    driver.quit()
    kwargs['ti'].xcom_push(key='all_links', value=all_links)
    return all_links


def extract_data(**kwargs):
    ti = kwargs['ti']
    bank_urls_dict = ti.xcom_pull(task_ids="extract_links", key='all_links')
    driver = initialize_driver()
    all_data = []

    for search_url, bank_urls in bank_urls_dict.items():
        print(f"Processing URLs from: {search_url}")

        # Set correct bank name based on search_url
        if "umnia" in search_url:
            bank_name = "umnia Bank"
        elif "bank+pop" in search_url:
            bank_name = "Banque Populaire"
        else:
            bank_name = "Unknown Bank"

        for index, url in enumerate(bank_urls, start=1):
            print(f"🔍 Scraping de l'URL {index}: {url}")
            driver.get(url)
            time.sleep(5)

            # Extract bank address
            try:
                address_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.Io6YTe.fontBodyMedium.kR99db.fdkmkc"))
                )
                address = address_element.text.strip()
            except TimeoutException:
                address = "Non trouvée"

            # Click on "Avis" button to reveal reviews
            try:
                buttons = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.RWPxGd button"))
                )
                buttons[1].click()
                time.sleep(5)
            except (TimeoutException, IndexError):
                print(f"⚠️ 'Avis' button not found for {bank_name}")

            # Extract reviews
            def extract_reviews():
                reviews = driver.find_elements(By.CSS_SELECTOR, "div.MyEned span.wiI7pd")
                return [review.text for review in reviews]

            all_reviews = set()
            scroll_count = 0
            max_scrolls = 2
            retry_count = 0

            while scroll_count < max_scrolls:
                current_reviews = extract_reviews()
                unique_reviews = set(current_reviews) - all_reviews
                all_reviews.update(unique_reviews)

                print(f"Scroll {scroll_count + 1}: Found {len(unique_reviews)} new reviews.")

                try:
                    scrollable_element = driver.find_element(By.CSS_SELECTOR, "div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde")
                    driver.execute_script("arguments[0].scrollTop += 2000", scrollable_element)
                    time.sleep(3)
                except Exception as e:
                    print(f"⚠️ Error during scrolling: {e}")

                try:
                    WebDriverWait(driver, 10).until(
                        lambda d: len(extract_reviews()) > len(current_reviews)
                    )
                except Exception:
                    print("⚠️ No new reviews loaded after scrolling. Retrying...")
                    retry_count += 1
                    if retry_count > 3:
                        break
                    time.sleep(10)

                scroll_count += 1

            reviews = list(all_reviews)

            # Extract review dates and ratings
            try:
                date_elements = driver.find_elements(By.CSS_SELECTOR, "span.rsqaWe")
                rating_elements = driver.find_elements(By.CSS_SELECTOR, "span.kvMYJc")

                dates = [date.text.strip() for date in date_elements]
                ratings = [len(r.find_elements(By.CLASS_NAME, "elGi1d")) for r in rating_elements]
            except Exception as e:
                print(f"⚠️ Error extracting review details: {e}")
                continue

            # Store extracted data
            for i in range(len(reviews)):
                try:
                    all_data.append({
                        "bank_name": bank_name,
                        "branche_name": bank_name + " " + address,
                        "address": address,
                        "review": reviews[i],
                        "rating": ratings[i] if i < len(ratings) else "N/A",
                        "review_date": dates[i] if i < len(dates) else "N/A"
                    })
                except Exception as e:
                    print(f"⚠️ Error processing review: {e}")

    driver.quit()
    kwargs['ti'].xcom_push(key='scraped_data', value=all_data)
    return all_data


# Task to insert data into the database
def translate_text_if_needed(text):
    """
    Detect language and translate if it's not French.
    """
    try:
        detected_lang = detect(text)  # Detect language
        if detected_lang == "fr":
            return text  # Keep the text if it's in French
        else:
            translator = Translator()
            translated = translator.translate(text, src=detected_lang, dest='en')
            return translated.text  # Return translated text
    except Exception as e:
        print(f"⚠️ Error detecting/translating text: {text}. Error: {e}")
        return text  # Fallback to the original text if an error occurs


def translate_text(text, source_lang='auto', target_lang='en'):
    """
    Helper function to translate text from a source language to a target language.
    """
    try:
        translated_text = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
        print(f"🌐 Original: {text}")
        print(f"🌐 Translated: {translated_text}")
        return translated_text
    except Exception as e:
        print(f"⚠️ Error translating text: {e}")
        return text  # Fallback to the original text if translation fails





def detect_language(text):
    try:
        return detect(text)
    except Exception as e:
        print(f"⚠️ Erreur lors de la détection de la langue: {e}")
        return "unknown"  # Retourner "unknown" en cas d'erreur
    



def insert_data_into_db(**kwargs):
    ti = kwargs['ti']
    scraped_data = ti.xcom_pull(task_ids='extract_data', key='scraped_data')
    print("got data ", scraped_data)
    
    if scraped_data:
        df = pd.DataFrame(scraped_data)
        sql_alchemy_conn = "postgresql+psycopg2://airflow_user:pass1234@localhost:5432/airflow_db"
        engine = create_engine(sql_alchemy_conn)
        try:
            # Iterate over each row in the DataFrame
            for index, row in df.iterrows():
                # Translate all fields
                bank_name = row['bank_name']
                branche_name = row['branche_name']
                translated_review = translate_text_if_needed(row['review'])
                address = row['address']
                translated_date = translate_text(row['review_date'])
                rating = row['rating']

                    
                numbers = re.findall(r'\d+', translated_date)
                if numbers:
                    numbers = [int(num) for num in numbers]
                else:
                    numbers = [0]  # Default value to avoid index error


                
                
                sysdate = datetime.today()
                past_date = sysdate  # Default case

                if numbers[0] > 0:  # Only modify date if a valid number was found
                    if "year" in translated_date:
                        past_date = sysdate.replace(year=sysdate.year - numbers[0])
                    elif "month" in translated_date:
                        month_offset = numbers[0]
                        if sysdate.month > month_offset:
                            past_date = sysdate.replace(month=sysdate.month - month_offset)
                        else:
                            past_date = sysdate.replace(year=sysdate.year - 1, month=12 + (sysdate.month - month_offset))
                    elif "day" in translated_date:
                        past_date = sysdate - timedelta(days=numbers[0])

                print(f"📅 Translated Date: {translated_date}, Extracted Numbers: {numbers}")

                date = past_date.strftime("%Y-%m-%d")

                

                # Normalize the translated review text to remove extra spaces
                # Ensure translated_review is not None before processing

                # Ensure translated_review is not None or empty


                if translated_review and translated_review.strip():
                    normalized_review = " ".join(translated_review.split())
                else:
                    normalized_review = ""  # Assign an empty string if None or empty

                # Avoid errors in language detection and sentiment analysis
                # lang = detect(normalized_review) if normalized_review else "unknown"

                # Check if the review already exists in the database using a parameterized query
                query = text("""
                SELECT 1 FROM bank_agency_reviews 
                WHERE bank_name = :bank_name 
                AND branche_name = :branche_name 
                AND review = :review 
                AND review_date = :review_date;
                """)
                
                # Execute the query with parameters
                result = engine.execute(query, {
                    "bank_name": bank_name,
                    "branche_name": branche_name,
                    "review": normalized_review,
                    "review_date": date,
                    # "language" : lang
                }).fetchone()
                print()
                # If the review does not exist, insert it
                if not result:
                    # Update the row with the translated fields
                    row['bank_name'] = bank_name
                    row['branche_name'] = branche_name
                    row['review'] = normalized_review
                    row['address'] = address
                    row['rating'] = rating
                    # row['review_sentiment'] = review_sentiment
                    row['scrapping_date'] = datetime.now()
                    row['review_date'] = date

                    # Insert the row into the database
                    row.to_frame().T.to_sql('bank_agency_reviews', con=engine, if_exists='append', index=False)
                    print(f"✅ Inserted review: {normalized_review}")
                else:
                    print(f"⚠️ Review already exists: {normalized_review}")
            
            print("✅ Data insertion process completed!")
        except Exception as e:
            print(f"⚠️ Error inserting data into the database: {e}")
    else:
        print("⚠️ No data to insert into the database.")




# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

SQL_ALCHEMY_CONN = "postgresql+psycopg2://airflow_user:pass1234@localhost:5432/airflow_db"



def get_sentiment(review, sentiment_pipeline):
    result = sentiment_pipeline(review)[0]
    label = result['label']
    if "5" in label or "4" in label:
        return "Positive"
    elif "3" in label:
        return "Neutral"
    else:
        return "Negative"

def process_reviews():
    from transformers import pipeline
    from sqlalchemy import create_engine
    import pandas as pd
    from langdetect import detect
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation

    def detect_language(text):
        try:
            return detect(text)
        except:
            return "unknown"

    engine = create_engine(SQL_ALCHEMY_CONN)
    df = pd.read_sql("SELECT * FROM clean_bank_reviews", con=engine)

    if "review" not in df.columns or df["review"].isna().all():
        raise ValueError("The 'review' column is missing or contains only NaN values.")

    df["language"] = df["review"].fillna("").apply(detect_language)
    df = df[df["language"] != "unknown"]
    if df.empty:
        print("No valid reviews with detected language. Exiting.")
        return
    
    # Load the sentiment model once
    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model="nlptown/bert-base-multilingual-uncased-sentiment"
    )

    # Apply the sentiment analysis
    df["sentiment"] = df["review"].apply(lambda x: get_sentiment(x, sentiment_pipeline))

    try:
        valid_reviews = df["review"].dropna()
        vectorizer = CountVectorizer(stop_words="english")
        X = vectorizer.fit_transform(valid_reviews)

        lda = LatentDirichletAllocation(n_components=5, random_state=42)
        lda.fit(X)

        topics = lda.transform(X).argmax(axis=1)
        df.loc[df["review"].notnull(), "topic_number"] = topics

        feature_names = vectorizer.get_feature_names_out()
        
        topic_keywords = {
            topic_idx: [feature_names[i] for i in topic.argsort()[:-6:-1]]
            for topic_idx, topic in enumerate(lda.components_)
        }
        topic_labels = {
            idx: ", ".join(words)
            for idx, words in topic_keywords.items()
        }

        df["topic_words"] = df["topic_number"].apply(lambda x: topic_labels.get(int(x), "Unknown"))
        df["topic_meaning"] = df["topic_words"]

    except Exception as e:
        print(f"Topic modeling failed: {e}")
        df["topic_number"] = -1
        df["topic_words"] = "Unknown"
        df["topic_meaning"] = "Unknown"

    df.to_sql("final_reviews", con=engine, if_exists="replace", index=False)
    print("✅ Post-processing complete!")


# ////////////////////////////////////////////////////////////////////////


def copy_tables_to_remote():
    from sqlalchemy import create_engine
    import pandas as pd
    import traceback

    local_conn_str = "postgresql+psycopg2://airflow_user:pass1234@localhost:5432/airflow_db"
    remote_conn_str = "postgresql+psycopg2://avnadmin:AVNS_s_10Re1L6tSkheJD4iJ@pg-6216120-analysecustomerreviews.i.aivencloud.com:10762/defaultdb?sslmode=require"

    tables = ["dim_bank", "dim_branch", "dim_location", "dim_sentiment", "fact_reviews", "final_reviews"]
    schema = "public_decision_schema"
    schema_public = "public"

    local_engine = create_engine(local_conn_str)
    remote_engine = create_engine(remote_conn_str)

    for table in tables:
        try:
            source_schema = schema if table != "final_reviews" else schema_public
            
            print(f"🔄 Reading '{table}' from local schema '{source_schema}'...")

            # Use query for clean_bank_reviews to avoid reflection issues
            if table == "final_reviews":
                df = pd.read_sql_query(f"SELECT * FROM {source_schema}.{table}", con=local_engine)
            else:
                df = pd.read_sql_table(table, con=local_engine, schema=source_schema)

            print(f"⬆️ Uploading '{table}' to remote (replace if exists)...")
            df.to_sql(table, con=remote_engine, schema="public", index=False, if_exists="replace", method="multi")

            print(f"✅ '{table}' copied and replaced successfully.")
        except Exception as e:
            print(f"❌ Error copying '{table}': {e}")
            traceback.print_exc()




def save_data_to_csv(**kwargs):
    ti = kwargs['ti']
    scraped_data = ti.xcom_pull(task_ids='extract_data', key='scraped_data')
    if scraped_data:
        df = pd.DataFrame(scraped_data)
        df.to_csv("bank_reviews.csv", index=False, encoding="utf-8")
        print("✅ Data saved to 'bank_reviews.csv'.")


# Define the DAG
with DAG('scrape_and_insert_bank_reviews', 
         description='Scrape bank reviews and insert them into the DB',
         schedule_interval=None, 
         start_date=days_ago(1), 
         catchup=False) as dag:

    create_table_task = PythonOperator(
        task_id='create_table_if_not_exists',
        python_callable=create_table_if_not_exists,
    )

    extract_links_task = PythonOperator(
        task_id='extract_links',
        python_callable=extract_links,
        provide_context=True,
    )
    
    extract_data_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data,
        provide_context=True,
    )
    
    insert_data_task = PythonOperator(
        task_id='insert_data_into_db',
        python_callable=insert_data_into_db,
        provide_context=True,
    )

    save_data_to_csv_task = PythonOperator(
        task_id='save_data_csv',
        python_callable=save_data_to_csv,
        provide_context=True,
    )

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    run_clean_reviews = BashOperator(
        task_id="run_clean_reviews",
        bash_command="cd ~/airflow/dbt_project && dbt run --select clean_bank_reviews",
        dag=dag,
    )

    process_reviews_task = PythonOperator(
        task_id="process_reviews",
        python_callable=process_reviews,
        dag=dag,
    )

    run_decision_models = BashOperator(
        task_id="run_decision_models",
        bash_command="cd ~/airflow/dbt_project/models/decision_schema && dbt run",
        dag=dag,
    )

    # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    transfer_data_to_looker = PythonOperator(
        task_id="copy_tables_to_remote",
        python_callable = copy_tables_to_remote,
        dag=dag,
    )

    
    # Task dependencies
    create_table_task >> extract_links_task >> extract_data_task >> insert_data_task >> save_data_to_csv_task >> run_clean_reviews >> process_reviews_task >> run_decision_models >> transfer_data_to_looker



