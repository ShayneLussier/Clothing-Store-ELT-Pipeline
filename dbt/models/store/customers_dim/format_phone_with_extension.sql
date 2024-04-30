SELECT
    id AS TRANSACTION_ID,
    CONCAT(
        SUBSTRING(REGEXP_REPLACE(SUBSTRING(customer:phone, 1, POSITION('x' IN customer:phone) - 1), '[^0-9]', ''), GREATEST(LENGTH(REGEXP_REPLACE(SUBSTRING(customer:phone, 1, POSITION('x' IN customer:phone) - 1), '[^0-9]', '')) - 9, 1), 3), '-',
        SUBSTRING(REGEXP_REPLACE(SUBSTRING(customer:phone, 1, POSITION('x' IN customer:phone) - 1), '[^0-9]', ''), GREATEST(LENGTH(REGEXP_REPLACE(SUBSTRING(customer:phone, 1, POSITION('x' IN customer:phone) - 1), '[^0-9]', '')) - 6, 1), 3), '-',
        SUBSTRING(REGEXP_REPLACE(SUBSTRING(customer:phone, 1, POSITION('x' IN customer:phone) - 1), '[^0-9]', ''), GREATEST(LENGTH(REGEXP_REPLACE(SUBSTRING(customer:phone, 1, POSITION('x' IN customer:phone) - 1), '[^0-9]', '')) - 3, 1), 4)
        ) AS PHONE
FROM {{ source('store_staging', 'raw_data') }}