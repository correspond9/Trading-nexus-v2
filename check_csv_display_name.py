#!/usr/bin/env python3
"""Check CSV data for DISPLAY_NAME values"""

import csv

csv_path = 'instrument_master/api-scrip-master-detailed.csv'

# Read the CSV and show a few equity rows
with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
    reader = csv.DictReader(f)
    count = 0
    for row in reader:
        if row.get('INSTRUMENT', '').upper() == 'EQUITY':
            count += 1
            if count <= 5:
                print(f'Row {count}:')
                print(f'  SYMBOL_NAME: {row.get("SYMBOL_NAME")}')
                print(f'  DISPLAY_NAME: {row.get("DISPLAY_NAME")}')
                print(f'  UNDERLYING_SYMBOL: {row.get("UNDERLYING_SYMBOL")}')
                print()
            if count >= 5:
                break
    
print(f'Total equity rows checked: {count}')
