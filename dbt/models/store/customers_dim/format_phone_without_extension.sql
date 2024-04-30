SELECT
    id AS TRANSACTION_ID,
    CONCAT(
        SUBSTRING(REGEXP_REPLACE(customer:phone, '[^0-9]', ''), GREATEST(LENGTH(REGEXP_REPLACE(customer:phone, '[^0-9]', '')) - 9, 1), 3), '-',
        SUBSTRING(REGEXP_REPLACE(customer:phone, '[^0-9]', ''), GREATEST(LENGTH(REGEXP_REPLACE(customer:phone, '[^0-9]', '')) - 6, 1), 3), '-',
        SUBSTRING(REGEXP_REPLACE(customer:phone, '[^0-9]', ''), GREATEST(LENGTH(REGEXP_REPLACE(customer:phone, '[^0-9]', '')) - 3, 1), 4)
        ) AS PHONE
FROM {{ source('store_staging', 'raw_data') }}