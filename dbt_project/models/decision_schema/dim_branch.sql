-- dim_bank.sql
{{ config(materialized='table') }}

WITH source AS (
    SELECT DISTINCT branche_name
    FROM {{ source('public', 'final_reviews') }}
)

SELECT 
    ROW_NUMBER() OVER () AS branch_id,
    branche_name
FROM source
