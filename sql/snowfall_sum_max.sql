SELECT time, snowfall_sum
FROM daily
ORDER BY snowfall_sum DESC
LIMIT 10;