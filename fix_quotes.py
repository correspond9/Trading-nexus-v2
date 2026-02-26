#!/usr/bin/env python3
# Fix smart quotes in admin.py

with open('app/routers/admin.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all smart quotes with regular ones
replacements = [
    ('\u2018', "'"),  # left single quotation mark
    ('\u2019', "'"),  # right single quotation mark
    ('\u201c', '"'),   # left double quotation mark
    ('\u201d', '"'),   # right double quotation mark
    ('\u2013', '-'),   # en dash
    ('\u2014', '-'),   # em dash
    ('\u2026', '...'), # ellipsis
]

count = 0
for smart, regular in replacements:
    if smart in content:
        replaces = content.count(smart)
        content = content.replace(smart, regular)
        count += replaces
        print(f'Replaced {replaces} instance(s) of {repr(smart)} with {repr(regular)}')

# Write back
with open('app/routers/admin.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\nTotal replacements: {count}')
print('File saved.')
