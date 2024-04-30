SELECT
    id AS TRANSACTION_ID,
    customer:id AS CUSTOMER_ID,
    store_id AS STORE_ID,
    date AS TRANSACTION_DATE,
    flattened.key AS ITEM_ID,
    flattened.value:product_id::string AS PRODUCT_ID,
    flattened.value:price::decimal(10, 2) AS ITEM_PRICE
FROM {{ source('store_staging', 'raw_data') }},
LATERAL FLATTEN(input => items) AS flattened
WHERE ARRAY_SIZE(items) > 0