# zagarolo-hystorical-weather-data
Zagarolo historical weather data

## Scripts Available

### global_downloader.py
Global downloader application that downloads historical weather data from 1945 onwards for Zagarolo using the Open-Meteo API. 

**Quick start:**
```bash
# Download all data from 1945 to present (daily data only, JSON format)
python global_downloader.py

# Check what years are already downloaded
python global_downloader.py --check-existing
```

See [GLOBAL_DOWNLOADER.md](GLOBAL_DOWNLOADER.md) for detailed documentation.

### openmeteo_downloader.py  
Single-year weather data downloader with full control over parameters.

### Database Tools
- `create_weather_db.py` - Create SQLite database structure
- `import_weather_json_to_sqlite.py` - Import JSON weather data to SQLite

## Default Location
Coordinates for Zagarolo: latitude=41.837610, longitude=12.831867
