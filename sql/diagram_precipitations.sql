.headers on
.mode json
.output precipitations_per_year.json
SELECT 
    substr(time, 1, 4) AS anno,
    ROUND(SUM(precipitation_sum), 0) AS totale_precipitazioni
FROM 
    daily
GROUP BY 
    anno
ORDER BY 
    time ASC;