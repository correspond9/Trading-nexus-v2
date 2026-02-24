#!/usr/bin/env python3
import os

export_file = 'data_export.sql'

with open(export_file, 'r', encoding='utf-8') as f:
    content = f.read()

inserts = content.count('INSERT INTO')
copies = content.count('COPY')
size_mb = len(content) / 1024 / 1024

print('Export Analysis:')
print(f'  INSERT statements: {inserts}')
print(f'  COPY sections: {copies}')
print(f'  File size: {size_mb:.2f} MB')
print(f'  Has data: {"Yes" if inserts > 0 or copies > 0 else "No"}')

# Get file lines for COPY data extraction
lines = content.split('\n')
copy_start = -1
for i, line in enumerate(lines):
    if line.startswith('COPY'):
        copy_start = i
        print(f'\nCOPY data found at line {i+1}')
        print(f'Sample: {line[:100]}...')
        break
