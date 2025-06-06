{{
  config(
    materialized='table'
  )
}}

WITH source AS (
    SELECT 
        review,
        review_date,
        rating,
        scrapping_date,
        TRIM(bank_name) AS bank_name,
        TRIM(branche_name) AS branche_name,
        TRIM(address) AS address,
        TRIM(sentiment) AS sentiment,
        topic_meaning,
        topic_words
    FROM {{ source('public', 'final_reviews') }}
),

bank_dim AS (
    SELECT 
        TRIM(bank_name) AS bank_name,
        ROW_NUMBER() OVER () AS bank_id
    FROM (SELECT DISTINCT TRIM(bank_name) AS bank_name FROM source) AS subquery
),

branch_dim AS (
    SELECT 
        TRIM(branche_name) AS branche_name,
        ROW_NUMBER() OVER () AS branch_id
    FROM (SELECT DISTINCT TRIM(branche_name) AS branche_name FROM source) AS subquery
),

location_dim AS (
    SELECT 
        TRIM(address) AS address,
        ROW_NUMBER() OVER () AS location_id
    FROM (SELECT DISTINCT TRIM(address) AS address FROM source) AS subquery
),

sentiment_dim AS (
    SELECT 
        TRIM(sentiment) AS sentiment,
        ROW_NUMBER() OVER () AS sentiment_id
    FROM (SELECT DISTINCT TRIM(sentiment) AS sentiment FROM source) AS subquery
)

SELECT 
    bank_dim.bank_id, 
    branch_dim.branch_id, 
    location_dim.location_id, 
    sentiment_dim.sentiment_id, 
    source.review_date,
    source.scrapping_date,
    source.review AS review_text,
    source.topic_meaning,
    source.topic_words,
    source.rating
FROM source
LEFT JOIN bank_dim ON TRIM(source.bank_name) = TRIM(bank_dim.bank_name)
LEFT JOIN branch_dim ON TRIM(source.branche_name) = TRIM(branch_dim.branche_name)
LEFT JOIN location_dim ON TRIM(source.address) = TRIM(location_dim.address)
LEFT JOIN sentiment_dim ON TRIM(source.sentiment) = TRIM(sentiment_dim.sentiment)
