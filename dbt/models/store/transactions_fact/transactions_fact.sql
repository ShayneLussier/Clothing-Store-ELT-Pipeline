{% if target.name == 'dev' %}
    {{ config(
        materialized='view',
    ) }}
{% elif target.name == 'prod' %}
    {{ config(
        materialized='incremental',
    ) }}
{% endif %}

WITH flattened_items_array_data AS (
    SELECT * FROM {{ ref('flattened_items_array') }}
),

final AS (
    SELECT
        CONCAT(TRANSACTION_ID, '-', ROW_NUMBER() OVER (PARTITION BY TRANSACTION_ID ORDER BY item_id)) AS TRANSACTION_ITEM_ID,
        TRANSACTION_ID,
        CUSTOMER_ID,
        STORE_ID,
        TRANSACTION_DATE,
        PRODUCT_ID,
        ITEM_PRICE  ,
        SUM(ITEM_PRICE  ) OVER (PARTITION BY TRANSACTION_ID) AS total_price
    FROM flattened_items_array_data
)

SELECT * FROM final