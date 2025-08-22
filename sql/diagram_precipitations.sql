.headers on
.mode json
.output ../precipitations_per_year.json
SELECT 
    substr(time, 1, 4) AS anno,
    CAST(ROUND(SUM(precipitation_sum), 0) AS INTEGER) AS totale_precipitazioni,
    CAST(ROUND(SUM(snowfall_sum), 1) AS INTEGER) AS totale_neve
FROM 
    daily
GROUP BY 
    anno
ORDER BY 
    time ASC;