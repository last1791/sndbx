#!/usr/bin/env python3
import json
import ftplib
from pathlib import Path
import os

FTP_HOST = os.getenv('FTP_HOST')
FTP_USER = os.getenv('FTP_USER')
FTP_PASS = os.getenv('FTP_PASS')
FTP_DIR  = os.getenv('FTP_DIR', '/')

# Soubory k nahrání: (lokální cesta, vzdálený název)
FILES = [
    (Path('sndbx/ai-news.jsonl'),   'ai-news.jsonl'),
    (Path('sndbx/llm_data.jsonl'),  'llm_data.jsonl'),
]

def upload_files_to_ftp():
    with ftplib.FTP_TLS(FTP_HOST) as ftp:
        ftp.login(FTP_USER, FTP_PASS)
        ftp.cwd(FTP_DIR)

        for local_file, remote_name in FILES:
            if not local_file.exists():
                print(f"Přeskočeno (neexistuje): {local_file}")
                continue
            with open(local_file, 'rb') as f:
                ftp.storbinary(f'STOR {remote_name}', f)
            print(f"Nahráno: {local_file} → {FTP_HOST}{FTP_DIR}/{remote_name}")

if __name__ == '__main__':
    upload_files_to_ftp()
