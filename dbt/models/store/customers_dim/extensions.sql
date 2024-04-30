SELECT
    id AS TRANSACTION_ID,
    CASE WHEN POSITION('x' IN customer:phone) > 0 THEN
        CASE WHEN LENGTH(customer:phone) - POSITION('x' IN customer:phone) > 1 THEN 
            SUBSTRING(customer:phone, POSITION('x' IN customer:phone) + 1)
        ELSE NULL END
    ELSE NULL END AS EXTENSION
FROM {{ source('store_staging', 'raw_data') }}