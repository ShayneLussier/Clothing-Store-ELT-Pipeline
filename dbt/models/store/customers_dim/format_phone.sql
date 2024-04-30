SELECT
    rd.id AS TRANSACTION_ID,
    CASE WHEN POSITION('x' IN rd.customer:phone) > 0 THEN 
        ext_with.PHONE
    ELSE 
        ext_without.PHONE
    END AS PHONE
FROM {{ source('store_staging', 'raw_data') }} AS rd
LEFT JOIN {{ ref('format_phone_with_extension') }} AS ext_with ON rd.id = ext_with.transaction_id
LEFT JOIN {{ ref('format_phone_without_extension') }} AS ext_without ON rd.id = ext_without.transaction_id
