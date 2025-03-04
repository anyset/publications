WITH sales_by_product_type AS (
    SELECT
        client_id,
        IF(product_type = 'MEUBLE', prod_price * prod_qty, 0) AS ventes_meuble,
        IF(product_type = 'DECO',  prod_price * prod_qty, 0) AS ventes_deco
    FROM TRANSACTION t
    JOIN PRODUCT_NOMENCLATURE pn
        ON pn.product_id = t.product_id
    WHERE TO_DATE(date, 'dd/MM/yy') >= "2019-01-01" AND TO_DATE(date, 'dd/MM/yy') < "2020-01-01"
)

SELECT client_id, SUM(ventes_meuble) AS ventes_meuble, SUM(ventes_deco) AS ventes_deco
FROM sales_by_product_type
GROUP BY client_id