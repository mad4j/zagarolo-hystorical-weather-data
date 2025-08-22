SELECT 
    substr(time, 1, 4) AS anno, 
    SUM(precipitation_sum) AS totale_precipitazioni
FROM 
    daily
GROUP BY 
    anno
ORDER BY 
    totale_precipitazioni DESC
LIMIT 10;