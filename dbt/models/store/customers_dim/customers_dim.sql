{% if target.name == 'dev' %}
    {{ config(
        materialized='view',
    ) }}
{% elif target.name == 'prod' %}
    {{ config(
        materialized='incremental',
    ) }}
{% endif %}

WITH extensions AS (
    SELECT * FROM {{ ref('extensions') }}
),

phone AS (
    SELECT * FROM {{ ref('format_phone') }}
),

final AS (
    SELECT DISTINCT
        rd.customer:id AS CUSTOMER_ID,
        SPLIT_PART(rd.customer:name, ' ', 1) AS FIRST_NAME,
        SPLIT_PART(rd.customer:name, ' ', 2) AS LAST_NAME,
        rd.customer:email AS EMAIL,
        p.phone AS PHONE,
        e.extension AS EXTENSION,
        rd.customer:address AS ADDRESS,
        rd.customer:card_number AS CARD_NUMBER
    FROM 
        {{ source('store_staging', 'raw_data') }} AS rd
    LEFT JOIN 
        extensions AS e ON rd.id = e.transaction_id
    LEFT JOIN
        phone AS p ON rd.id = p.transaction_id
)

SELECT * FROM final