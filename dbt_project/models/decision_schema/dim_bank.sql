-- dim_bank.sql
{{ config(materialized='table') }}

WITH source AS (
    SELECT DISTINCT bank_name
    FROM {{ source('public', 'final_reviews') }}
)

SELECT 
    ROW_NUMBER() OVER () AS bank_id,
    bank_name
FROM source