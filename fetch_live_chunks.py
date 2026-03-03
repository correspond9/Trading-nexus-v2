import requests
from pathlib import Path

base = 'https://tradingnexus.pro/'
chunks = [
    'assets/Profile-D6Sveqqp.js',
    'assets/SuperAdmin-BhL9KGJZ.js'
]
out_dir = Path('tmp_live_chunks')
out_dir.mkdir(exist_ok=True)

for chunk in chunks:
    url = base + chunk
    text = requests.get(url, timeout=30).text
    p = out_dir / chunk.split('/')[-1]
    p.write_text(text, encoding='utf-8')
    print(f'saved {p} len={len(text)}')
