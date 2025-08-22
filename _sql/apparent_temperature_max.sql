SELECT time, apparent_temperature_max, temperature_2m_max, temperature_2m_min
FROM daily
ORDER BY apparent_temperature_max DESC
LIMIT 10;