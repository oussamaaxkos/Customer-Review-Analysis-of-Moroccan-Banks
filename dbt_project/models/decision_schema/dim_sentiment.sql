-- dim_bank.sql
{{ config(materialized='table') }}
WITH source AS (
    SELECT DISTINCT sentiment
    FROM {{ source('public', 'final_reviews') }}
)

SELECT 
    ROW_NUMBER() OVER () AS sentiment_id,
    sentiment AS sentiment_label
FROM source