# Global Downloader per Dati Meteo Storici di Zagarolo

Questo script (`global_downloader.py`) permette di scaricare automaticamente i dati meteo storici dal 1945 ad oggi per Zagarolo utilizzando l'API Open-Meteo.

## Caratteristiche

- **Scarica automaticamente** tutti gli anni dal 1945 al presente
- **Coordinate predefinite** per Zagarolo: latitude=41.837610, longitude=12.831867
- **Solo dati giornalieri** (no dati orari) in formato JSON
- **Gestione errori** e ripresa automatica
- **Progresso** e logging dettagliato
- **Controllo file esistenti** per evitare download duplicati

## Utilizzo

### Download completo (1945-presente)
```bash
python global_downloader.py
```

### Download di un periodo specifico
```bash
# Dal 2000 ad oggi
python global_downloader.py --start-year 2000

# Dal 1945 al 2020
python global_downloader.py --end-year 2020

# Solo anni 2000-2010
python global_downloader.py --start-year 2000 --end-year 2010
```

### Riprendere download interrotto
```bash
# Riprende dal 2010 (utile se il download si è interrotto)
python global_downloader.py --resume-from 2010
```

### Controllare file già scaricati
```bash
python global_downloader.py --check-existing
```

### Coordinate personalizzate
```bash
python global_downloader.py --latitude 45.0 --longitude 9.0
```

## Parametri Disponibili

- `--latitude`: Latitudine (default: 41.83761 per Zagarolo)
- `--longitude`: Longitudine (default: 12.831867 per Zagarolo)
- `--output-dir`: Directory di output (default: weather_data)
- `--start-year`: Anno di inizio (default: 1945)
- `--end-year`: Anno finale (default: anno corrente)
- `--resume-from`: Anno da cui riprendere il download
- `--check-existing`: Mostra solo gli anni già scaricati

## File di Output

I file vengono salvati nella directory `weather_data/` con il formato:
```
weather_ANNO_LATITUDINE_LONGITUDINE.json
```

Esempio: `weather_2023_41.83761_12.831867.json`

## Dipendenze

Il global downloader utilizza lo script esistente `openmeteo_downloader.py` che deve essere presente nella stessa directory.

Dipendenze Python richieste:
- requests
- pandas

## Note

- Ogni anno viene scaricato separatamente per evitare timeout con l'API
- Il download include solo dati giornalieri (temperatura, precipitazioni, vento, ecc.)
- I file vengono salvati in formato JSON per facilità di elaborazione
- Lo script gestisce automaticamente i timeout e gli errori di rete
- È possibile interrompere il download con Ctrl+C e riprenderlo successivamente

## Esempio di Utilizzo Completo

```bash
# 1. Controlla se ci sono già file scaricati
python global_downloader.py --check-existing

# 2. Scarica tutti i dati dal 1945 ad oggi
python global_downloader.py

# 3. Se il download si interrompe, riprendi dall'ultimo anno
python global_downloader.py --resume-from 2020
```