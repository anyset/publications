SELECT date, sum(prod_price * prod_qty)
FROM TRANSACTION
WHERE TO_DATE(date, 'dd/MM/yy') >= "2019-01-01" AND TO_DATE(date, 'dd/MM/yy') < "01/01/20"
GROUP BY date
ORDER BY TO_DATE(date, 'dd/MM/yy')
