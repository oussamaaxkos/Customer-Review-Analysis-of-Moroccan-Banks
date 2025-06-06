-- dim_bank.sql
{{ config(materialized='table') }}

WITH source AS (
    SELECT DISTINCT address
    FROM {{ source('public', 'final_reviews') }}
)

SELECT 
    ROW_NUMBER() OVER () AS location_id,
    address
FROM source
