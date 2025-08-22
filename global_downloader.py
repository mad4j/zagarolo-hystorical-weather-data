#!/usr/bin/env python3
"""
Global Weather Data Downloader for Zagarolo
Scarica dati meteo storici dal 1945 in poi utilizzando openmeteo_downloader.py

Utilizza le coordinate predefinite per Zagarolo: latitude=41.837610, longitude=12.831867
Scarica solo dati giornalieri in formato JSON.
"""

import subprocess
import sys
import os
import logging
import time
import random
from datetime import datetime
from typing import Optional
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GlobalDownloader:
    """Downloader globale per dati meteo storici di Zagarolo"""
    
    # Coordinate predefinite per Zagarolo
    DEFAULT_LATITUDE = 41.837610
    DEFAULT_LONGITUDE = 12.831867
    
    # Anno di inizio predefinito
    START_YEAR = 1945
    
    def __init__(self, 
                 latitude: float = DEFAULT_LATITUDE, 
                 longitude: float = DEFAULT_LONGITUDE,
                 output_dir: str = "weather_data",
                 start_year: int = START_YEAR,
                 enable_pause: bool = True):
        self.latitude = latitude
        self.longitude = longitude
        self.output_dir = output_dir
        self.start_year = start_year
        self.current_year = datetime.now().year
        self.downloader_script = "openmeteo_downloader.py"
        self.enable_pause = enable_pause
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
    def download_year(self, year: int) -> bool:
        """
        Scarica i dati per un singolo anno
        
        Args:
            year: Anno da scaricare
            
        Returns:
            True se il download è riuscito, False altrimenti
        """
        logger.info(f"Scaricando dati per l'anno {year}...")
        
        cmd = [
            sys.executable,  # Usa lo stesso interprete Python
            self.downloader_script,
            str(self.latitude),
            str(self.longitude),
            str(year),
            "--no-hourly",  # Solo dati giornalieri
            "--formats", "json",  # Solo formato JSON
            "--output-dir", self.output_dir
        ]
        
        try:
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=300)  # Timeout di 5 minuti per anno
            
            if result.returncode == 0:
                logger.info(f"Anno {year} scaricato con successo")
                return True
            else:
                logger.error(f"Errore nel download dell'anno {year}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout durante il download dell'anno {year}")
            return False
        except Exception as e:
            logger.error(f"Errore imprevisto durante il download dell'anno {year}: {e}")
            return False
    
    def download_all(self, 
                     end_year: Optional[int] = None,
                     resume_from: Optional[int] = None) -> tuple[int, int]:
        """
        Scarica tutti i dati dal start_year all'end_year
        
        Args:
            end_year: Anno finale (default: anno corrente)
            resume_from: Anno da cui riprendere il download (default: start_year)
            
        Returns:
            Tupla (successi, fallimenti)
        """
        if end_year is None:
            end_year = self.current_year
            
        if resume_from is None:
            resume_from = self.start_year
            
        total_years = end_year - resume_from + 1
        successful = 0
        failed = 0
        
        logger.info(f"Inizio download globale: anni {resume_from}-{end_year} ({total_years} anni)")
        logger.info(f"Coordinate: {self.latitude}, {self.longitude}")
        logger.info(f"Directory di output: {self.output_dir}")
        
        for year in range(resume_from, end_year + 1):
            try:
                if self.download_year(year):
                    successful += 1
                else:
                    failed += 1
                    
                # Progress logging
                completed = year - resume_from + 1
                progress = (completed / total_years) * 100
                logger.info(f"Progresso: {completed}/{total_years} anni ({progress:.1f}%)")
                
                # Add variable pause between downloads (except for the last year)
                if self.enable_pause and completed < total_years:
                    pause_time = random.randint(5, 35)
                    logger.info(f"Pausa di {pause_time} secondi prima del prossimo download...")
                    time.sleep(pause_time)
                
            except KeyboardInterrupt:
                logger.info("Download interrotto dall'utente")
                break
            except Exception as e:
                logger.error(f"Errore imprevisto: {e}")
                failed += 1
                
        logger.info(f"Download completato: {successful} successi, {failed} fallimenti")
        return successful, failed
    
    def check_existing_files(self) -> list[int]:
        """
        Controlla quali anni sono già stati scaricati
        
        Returns:
            Lista degli anni già scaricati
        """
        existing_years = []
        
        if not os.path.exists(self.output_dir):
            return existing_years
            
        for filename in os.listdir(self.output_dir):
            if filename.startswith("weather_") and filename.endswith(".json"):
                # Format: weather_YEAR_LAT_LON.json
                parts = filename.split("_")
                if len(parts) >= 2:
                    try:
                        year = int(parts[1])
                        existing_years.append(year)
                    except ValueError:
                        continue
                        
        return sorted(existing_years)


def main():
    """Funzione principale con interfaccia a riga di comando"""
    
    parser = argparse.ArgumentParser(
        description='Downloader globale per dati meteo storici di Zagarolo (1945-presente)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  %(prog)s                          # Scarica dal 1945 ad oggi
  %(prog)s --start-year 2000        # Scarica dal 2000 ad oggi  
  %(prog)s --end-year 2020          # Scarica dal 1945 al 2020
  %(prog)s --resume-from 2010       # Riprende dal 2010
  %(prog)s --check-existing         # Mostra solo gli anni già scaricati
  %(prog)s --no-pause              # Disabilita la pausa tra download
        """
    )
    
    parser.add_argument('--latitude', type=float, 
                       default=GlobalDownloader.DEFAULT_LATITUDE,
                       help=f'Latitudine (default: {GlobalDownloader.DEFAULT_LATITUDE})')
    
    parser.add_argument('--longitude', type=float,
                       default=GlobalDownloader.DEFAULT_LONGITUDE, 
                       help=f'Longitudine (default: {GlobalDownloader.DEFAULT_LONGITUDE})')
    
    parser.add_argument('--output-dir', type=str, default='weather_data',
                       help='Directory di output (default: weather_data)')
    
    parser.add_argument('--start-year', type=int, 
                       default=GlobalDownloader.START_YEAR,
                       help=f'Anno di inizio (default: {GlobalDownloader.START_YEAR})')
    
    parser.add_argument('--end-year', type=int,
                       help='Anno finale (default: anno corrente)')
    
    parser.add_argument('--resume-from', type=int,
                       help='Anno da cui riprendere il download')
    
    parser.add_argument('--check-existing', action='store_true',
                       help='Mostra gli anni già scaricati e esce')
    
    parser.add_argument('--no-pause', action='store_true',
                       help='Disabilita la pausa tra i download (utile per test)')
    
    args = parser.parse_args()
    
    # Crea il downloader
    downloader = GlobalDownloader(
        latitude=args.latitude,
        longitude=args.longitude,
        output_dir=args.output_dir,
        start_year=args.start_year,
        enable_pause=not args.no_pause
    )
    
    # Controlla file esistenti se richiesto
    if args.check_existing:
        existing = downloader.check_existing_files()
        if existing:
            logger.info(f"Anni già scaricati: {existing}")
            logger.info(f"Totale: {len(existing)} anni")
        else:
            logger.info("Nessun file trovato")
        return
    
    # Verifica che lo script openmeteo_downloader.py esista
    if not os.path.exists(downloader.downloader_script):
        logger.error(f"Script {downloader.downloader_script} non trovato nella directory corrente")
        sys.exit(1)
    
    # Esegui il download
    successful, failed = downloader.download_all(
        end_year=args.end_year,
        resume_from=args.resume_from
    )
    
    if failed > 0:
        logger.warning(f"Download completato con {failed} errori")
        logger.info("Continuando comunque per permettere il commit dei dati "
                    "disponibili")
    else:
        logger.info("Download completato con successo!")


if __name__ == "__main__":
    main()
