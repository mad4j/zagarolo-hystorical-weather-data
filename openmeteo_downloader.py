#!/usr/bin/env python3
"""
Open-Meteo Historical Weather Data Downloader
Downloads all available historical weather data for a specific year and location
"""

import requests
import json
import csv
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import argparse
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpenMeteoDownloader:
    """Class to handle downloading historical weather data from Open-Meteo API"""
    
    BASE_URL = "https://archive-api.open-meteo.com/v1/archive"
    
    # All available hourly variables
    HOURLY_VARIABLES = [
        "temperature_2m",
        "relative_humidity_2m",
        "dew_point_2m",
        "apparent_temperature",
        "pressure_msl",
        "surface_pressure",
        "precipitation",
        "rain",
        "snowfall",
        "cloud_cover",
        "cloud_cover_low",
        "cloud_cover_mid",
        "cloud_cover_high",
        "shortwave_radiation",
        "direct_radiation",
        "direct_normal_irradiance",
        "diffuse_radiation",
        "sunshine_duration",
        "wind_speed_10m",
        "wind_speed_100m",
        "wind_direction_10m",
        "wind_direction_100m",
        "wind_gusts_10m",
        "soil_temperature_0_to_7cm",
        "soil_temperature_7_to_28cm",
        "soil_temperature_28_to_100cm",
        "soil_temperature_100_to_255cm",
        "soil_moisture_0_to_7cm",
        "soil_moisture_7_to_28cm",
        "soil_moisture_28_to_100cm",
        "soil_moisture_100_to_255cm"
    ]
    
    # All available daily variables
    DAILY_VARIABLES = [
        "weather_code",
        "temperature_2m_max",
        "temperature_2m_min",
        "apparent_temperature_max",
        "apparent_temperature_min",
        "precipitation_sum",
        "rain_sum",
        "snowfall_sum",
        "precipitation_hours",
        "sunrise",
        "sunset",
        "sunshine_duration",
        "daylight_duration",
        "wind_speed_10m_max",
        "wind_gusts_10m_max",
        "wind_direction_10m_dominant",
        "shortwave_radiation_sum",
        "et0_fao_evapotranspiration"
    ]
    
    def __init__(self, latitude: float, longitude: float, year: int, 
                 output_dir: str = "weather_data"):
        """
        Initialize the downloader
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            year: Year to download data for
            output_dir: Directory to save the downloaded data
        """
        self.latitude = latitude
        self.longitude = longitude
        self.year = year
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Set date range for the entire year
        self.start_date = f"{year}-01-01"
        self.end_date = f"{year}-12-31"
        
    def download_data(self, 
                     hourly_vars: Optional[List[str]] = None,
                     daily_vars: Optional[List[str]] = None,
                     timezone: str = "auto",
                     temperature_unit: str = "celsius",
                     wind_speed_unit: str = "kmh",
                     precipitation_unit: str = "mm") -> Dict:
        """
        Download weather data from Open-Meteo API
        
        Args:
            hourly_vars: List of hourly variables to download (None = all)
            daily_vars: List of daily variables to download (None = all)
            timezone: Timezone for the data
            temperature_unit: Temperature unit (celsius or fahrenheit)
            wind_speed_unit: Wind speed unit (kmh, ms, mph, kn)
            precipitation_unit: Precipitation unit (mm or inch)
            
        Returns:
            Dictionary containing the API response
        """
        # Use all variables if not specified
        if hourly_vars is None:
            hourly_vars = self.HOURLY_VARIABLES
        if daily_vars is None:
            daily_vars = self.DAILY_VARIABLES
            
        # Build the API request
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "timezone": timezone,
            "temperature_unit": temperature_unit,
            "wind_speed_unit": wind_speed_unit,
            "precipitation_unit": precipitation_unit
        }
        # Add 'hourly' only if requested
        if hourly_vars:
            params["hourly"] = ",".join(hourly_vars)
        # Add 'daily' always (empty list = no daily)
        params["daily"] = ",".join(daily_vars) if daily_vars is not None else ""
        
        logger.info(f"Downloading data for {self.year} at ({self.latitude}, {self.longitude})")
        logger.info(f"Date range: {self.start_date} to {self.end_date}")

        # Log the full request URL
        req = requests.Request('GET', self.BASE_URL, params=params).prepare()
        logger.info(f"Request URL: {req.url}")

        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info("Data downloaded successfully")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading data: {e}")
            raise
            
    def save_to_json(self, data: Dict, filename: Optional[str] = None):
        """Save data to JSON file"""
        if filename is None:
            filename = f"weather_{self.year}_{self.latitude}_{self.longitude}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Data saved to {filepath}")
        
    def save_hourly_to_csv(self, data: Dict, filename: Optional[str] = None):
        """Save hourly data to CSV file"""
        if filename is None:
            filename = f"weather_hourly_{self.year}_{self.latitude}_{self.longitude}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        if 'hourly' in data:
            # Convert to DataFrame for easier manipulation
            df = pd.DataFrame(data['hourly'])
            
            # Add metadata columns
            df['latitude'] = data['latitude']
            df['longitude'] = data['longitude']
            df['elevation'] = data['elevation']
            df['timezone'] = data['timezone']
            
            # Save to CSV
            df.to_csv(filepath, index=False)
            logger.info(f"Hourly data saved to {filepath}")
        else:
            logger.warning("No hourly data found in response")
            
    def save_daily_to_csv(self, data: Dict, filename: Optional[str] = None):
        """Save daily data to CSV file"""
        if filename is None:
            filename = f"weather_daily_{self.year}_{self.latitude}_{self.longitude}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        if 'daily' in data:
            # Convert to DataFrame
            df = pd.DataFrame(data['daily'])
            
            # Add metadata columns
            df['latitude'] = data['latitude']
            df['longitude'] = data['longitude']
            df['elevation'] = data['elevation']
            df['timezone'] = data['timezone']
            
            # Save to CSV
            df.to_csv(filepath, index=False)
            logger.info(f"Daily data saved to {filepath}")
        else:
            logger.warning("No daily data found in response")
            
    def save_metadata(self, data: Dict, filename: Optional[str] = None):
        """Save metadata and units information"""
        if filename is None:
            filename = f"weather_metadata_{self.year}_{self.latitude}_{self.longitude}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        metadata = {
            "latitude": data.get('latitude'),
            "longitude": data.get('longitude'),
            "elevation": data.get('elevation'),
            "timezone": data.get('timezone'),
            "timezone_abbreviation": data.get('timezone_abbreviation'),
            "utc_offset_seconds": data.get('utc_offset_seconds'),
            "generationtime_ms": data.get('generationtime_ms'),
            "hourly_units": data.get('hourly_units', {}),
            "daily_units": data.get('daily_units', {}),
            "year": self.year,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "download_timestamp": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Metadata saved to {filepath}")
        
    def check_existing_files(self, formats: List[str] = ['json', 'csv'], 
                            save_metadata: bool = False, 
                            include_hourly: bool = True,
                            include_daily: bool = True) -> List[str]:
        """
        Check which files already exist for this download configuration
        
        Args:
            formats: List of formats to check ('json', 'csv')
            save_metadata: Whether metadata file would be saved
            include_hourly: Whether hourly data would be included
            include_daily: Whether daily data would be included
            
        Returns:
            List of existing file paths
        """
        existing_files = []
        
        # Check JSON file
        if 'json' in formats:
            json_filename = f"weather_{self.year}_{self.latitude}_{self.longitude}.json"
            json_filepath = os.path.join(self.output_dir, json_filename)
            if os.path.exists(json_filepath):
                existing_files.append(json_filepath)
        
        # Check CSV files
        if 'csv' in formats:
            # Check hourly CSV (only if hourly data is included)
            if include_hourly:
                hourly_filename = f"weather_hourly_{self.year}_{self.latitude}_{self.longitude}.csv"
                hourly_filepath = os.path.join(self.output_dir, hourly_filename)
                if os.path.exists(hourly_filepath):
                    existing_files.append(hourly_filepath)
                
            # Check daily CSV (only if daily data is included)
            if include_daily:
                daily_filename = f"weather_daily_{self.year}_{self.latitude}_{self.longitude}.csv"
                daily_filepath = os.path.join(self.output_dir, daily_filename)
                if os.path.exists(daily_filepath):
                    existing_files.append(daily_filepath)
        
        # Check metadata file
        if save_metadata:
            metadata_filename = f"weather_metadata_{self.year}_{self.latitude}_{self.longitude}.json"
            metadata_filepath = os.path.join(self.output_dir, metadata_filename)
            if os.path.exists(metadata_filepath):
                existing_files.append(metadata_filepath)
        
        return existing_files
        
    def download_and_save_all(self, 
                             formats: List[str] = ['json', 'csv'],
                             **kwargs):
        """
        Download data and save in multiple formats
        
        Args:
            formats: List of formats to save ('json', 'csv')
            **kwargs: Additional arguments for download_data method
        """
        # Download data
        data = self.download_data(**kwargs)
        
        # Save in requested formats
        if 'json' in formats:
            self.save_to_json(data)
            
        if 'csv' in formats:
            self.save_hourly_to_csv(data)
            self.save_daily_to_csv(data)
            
        # Always save metadata
        self.save_metadata(data)
        
        logger.info(f"All data saved successfully in {self.output_dir}")
        return data


def download_chunked(latitude: float, longitude: float, year: int, 
                    output_dir: str = "weather_data",
                    chunk_size_months: int = 3):
    """
    Download data in chunks to avoid API limits for large requests
    
    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
        year: Year to download data for
        output_dir: Directory to save the downloaded data
        chunk_size_months: Number of months per chunk
    """
    all_data = []
    
    for month_start in range(1, 13, chunk_size_months):
        month_end = min(month_start + chunk_size_months - 1, 12)
        
        # Calculate date range
        start_date = f"{year}-{month_start:02d}-01"
        if month_end == 12:
            end_date = f"{year}-12-31"
        else:
            # Get last day of the month
            next_month = datetime(year, month_end + 1, 1)
            last_day = (next_month - timedelta(days=1)).day
            end_date = f"{year}-{month_end:02d}-{last_day:02d}"
        
        logger.info(f"Downloading chunk: {start_date} to {end_date}")
        
        # Create temporary downloader for this chunk
        temp_downloader = OpenMeteoDownloader(latitude, longitude, year, output_dir)
        temp_downloader.start_date = start_date
        temp_downloader.end_date = end_date
        
        try:
            data = temp_downloader.download_data()
            all_data.append(data)
            
            # Rate limiting
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error downloading chunk {start_date} to {end_date}: {e}")
            continue
    
    # Combine all chunks
    if all_data:
        combined_data = combine_chunks(all_data)
        
        # Save combined data
        downloader = OpenMeteoDownloader(latitude, longitude, year, output_dir)
        downloader.save_to_json(combined_data)
        downloader.save_hourly_to_csv(combined_data)
        downloader.save_daily_to_csv(combined_data)
        downloader.save_metadata(combined_data)
        
        logger.info("All chunks downloaded and combined successfully")
        return combined_data
    else:
        logger.error("No data was successfully downloaded")
        return None


def combine_chunks(chunks: List[Dict]) -> Dict:
    """Combine multiple data chunks into a single dataset"""
    if not chunks:
        return {}
    
    # Use first chunk as base
    combined = chunks[0].copy()
    
    # Combine hourly data
    if 'hourly' in combined:
        for chunk in chunks[1:]:
            if 'hourly' in chunk:
                for key in combined['hourly']:
                    if key in chunk['hourly']:
                        if isinstance(combined['hourly'][key], list):
                            combined['hourly'][key].extend(chunk['hourly'][key])
    
    # Combine daily data
    if 'daily' in combined:
        for chunk in chunks[1:]:
            if 'daily' in chunk:
                for key in combined['daily']:
                    if key in chunk['daily']:
                        if isinstance(combined['daily'][key], list):
                            combined['daily'][key].extend(chunk['daily'][key])
    
    return combined


def main():
    """Main function with command-line interface"""

    parser = argparse.ArgumentParser(
        description='Download historical weather data from Open-Meteo API'
    )

    parser.add_argument('latitude', type=float, help='Latitude of the location')
    parser.add_argument('longitude', type=float, help='Longitude of the location')
    parser.add_argument('year', type=int, help='Year to download data for')

    parser.add_argument('--output-dir', type=str, default='weather_data', help='Directory to save the downloaded data')
    parser.add_argument('--formats', nargs='+', default=['json', 'csv'], choices=['json', 'csv'], help='Output formats (default: json csv)')
    parser.add_argument('--timezone', type=str, default='auto', help='Timezone for the data (default: auto)')
    parser.add_argument('--temperature-unit', type=str, default='celsius', choices=['celsius', 'fahrenheit'], help='Temperature unit (default: celsius)')
    parser.add_argument('--wind-speed-unit', type=str, default='kmh', choices=['kmh', 'ms', 'mph', 'kn'], help='Wind speed unit (default: kmh)')
    parser.add_argument('--precipitation-unit', type=str, default='mm', choices=['mm', 'inch'], help='Precipitation unit (default: mm)')

    parser.add_argument('--chunked', action='store_true', help='Download data in chunks (useful for large requests)')
    parser.add_argument('--chunk-size', type=int, default=3, help='Number of months per chunk (default: 3)')

    # Mutually exclusive group for --no-hourly and --no-daily
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--no-hourly', action='store_true', help='Exclude hourly data from download')
    group.add_argument('--no-daily', action='store_true', help='Exclude daily data from download')

    parser.add_argument('--save-metadata', action='store_true', help='Save metadata file (default: do not save)')
    parser.add_argument('--force', action='store_true', help='Force download even if files already exist')

    args = parser.parse_args()

    logger.info(f"Starting download for year {args.year} at coordinates ({args.latitude}, {args.longitude})")

    # Determine which variables to download based on flags
    hourly_vars = None if not args.no_hourly else []
    daily_vars = None if not args.no_daily else []

    if args.chunked:
        # Check for existing files first unless force is specified
        if not args.force:
            downloader = OpenMeteoDownloader(
                args.latitude,
                args.longitude,
                args.year,
                args.output_dir
            )
            existing_files = downloader.check_existing_files(
                formats=args.formats,
                save_metadata=args.save_metadata,
                include_hourly=not args.no_hourly,
                include_daily=not args.no_daily
            )
            if existing_files:
                logger.info(f"Skipping download - files already exist: {existing_files}")
                logger.info("Use --force to override and download anyway")
                return
        
        # Download in chunks
        def patched_download_chunked(latitude, longitude, year, output_dir="weather_data", chunk_size_months=3, hourly_vars=None, daily_vars=None, **kwargs):
            all_data = []
            for month_start in range(1, 13, chunk_size_months):
                month_end = min(month_start + chunk_size_months - 1, 12)
                start_date = f"{year}-{month_start:02d}-01"
                if month_end == 12:
                    end_date = f"{year}-12-31"
                else:
                    next_month = datetime(year, month_end + 1, 1)
                    last_day = (next_month - timedelta(days=1)).day
                    end_date = f"{year}-{month_end:02d}-{last_day:02d}"
                logger.info(f"Downloading chunk: {start_date} to {end_date}")
                temp_downloader = OpenMeteoDownloader(latitude, longitude, year, output_dir)
                temp_downloader.start_date = start_date
                temp_downloader.end_date = end_date
                try:
                    data = temp_downloader.download_data(hourly_vars=hourly_vars, daily_vars=daily_vars, timezone=args.timezone, temperature_unit=args.temperature_unit, wind_speed_unit=args.wind_speed_unit, precipitation_unit=args.precipitation_unit)
                    all_data.append(data)
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Error downloading chunk {start_date} to {end_date}: {e}")
                    continue
            if all_data:
                combined_data = combine_chunks(all_data)
                downloader = OpenMeteoDownloader(latitude, longitude, year, output_dir)
                if 'json' in args.formats:
                    downloader.save_to_json(combined_data)
                if 'csv' in args.formats:
                    if not args.no_hourly:
                        downloader.save_hourly_to_csv(combined_data)
                    if not args.no_daily:
                        downloader.save_daily_to_csv(combined_data)
                if args.save_metadata:
                    downloader.save_metadata(combined_data)
                logger.info("All chunks downloaded and combined successfully")
                return combined_data
            else:
                logger.error("No data was successfully downloaded")
                return None
        patched_download_chunked(
            args.latitude,
            args.longitude,
            args.year,
            args.output_dir,
            args.chunk_size,
            hourly_vars=hourly_vars,
            daily_vars=daily_vars
        )
    else:
        # Check for existing files first unless force is specified
        if not args.force:
            downloader = OpenMeteoDownloader(
                args.latitude,
                args.longitude,
                args.year,
                args.output_dir
            )
            existing_files = downloader.check_existing_files(
                formats=args.formats,
                save_metadata=args.save_metadata,
                include_hourly=not args.no_hourly,
                include_daily=not args.no_daily
            )
            if existing_files:
                logger.info(f"Skipping download - files already exist: {existing_files}")
                logger.info("Use --force to override and download anyway")
                return
        
        # Download entire year at once
        downloader = OpenMeteoDownloader(
            args.latitude,
            args.longitude,
            args.year,
            args.output_dir
        )
        data = downloader.download_data(
            hourly_vars=hourly_vars,
            daily_vars=daily_vars,
            timezone=args.timezone,
            temperature_unit=args.temperature_unit,
            wind_speed_unit=args.wind_speed_unit,
            precipitation_unit=args.precipitation_unit
        )
        if 'json' in args.formats:
            downloader.save_to_json(data)
        if 'csv' in args.formats:
            if not args.no_hourly:
                downloader.save_hourly_to_csv(data)
            if not args.no_daily:
                downloader.save_daily_to_csv(data)
        if args.save_metadata:
            downloader.save_metadata(data)

    logger.info("Download completed successfully!")


if __name__ == "__main__":
    main()