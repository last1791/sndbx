#!/usr/bin/env python3
import json
import ftplib
from pathlib import Path
import os

# Nastavení FTP (použij secrets v GitHub Actions)
FTP_HOST = os.getenv('FTP_HOST')
FTP_USER = os.getenv('FTP_USER')
FTP_PASS = os.getenv('FTP_PASS')
FTP_DIR = os.getenv('FTP_DIR', '/')
REMOTE_FILE = 'ai-news.jsonl'

def upload_json_to_ftp():
    local_file = Path('sndbx/ai-news.jsonl')
    
    if not local_file.exists():
        print(f"Chyba: {local_file} neexistuje")
        return False
    
    # Připoj se na FTP
    with ftplib.FTP_TLS(FTP_HOST) as ftp:
        ftp.login(FTP_USER, FTP_PASS)
        ftp.cwd(FTP_DIR)
        
        # Nahraj soubor
        with open(local_file, 'rb') as f:
            ftp.storbinary(f'STOR {REMOTE_FILE}', f)
    
    print(f"Nahráno {local_file} na {FTP_HOST}{FTP_DIR}/{REMOTE_FILE}")
    return True

if __name__ == '__main__':
    upload_json_to_ftp()
