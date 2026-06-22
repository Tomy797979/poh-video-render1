#!/usr/bin/env python3
"""Parse danh sách Amazon URLs từ env var PRODUCTS → JSON matrix cho GitHub Actions."""
import json, os, re

raw = os.environ.get('PRODUCTS', '')
items = []
for line in raw.strip().splitlines():
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    if '|' in line:
        url, name = line.split('|', 1)
        url  = url.strip()
        name = re.sub(r'[^a-z0-9-]', '-', name.strip().lower()).strip('-')
    else:
        url  = line.strip()
        asin = re.search(r'[A-Z0-9]{10}', url)
        name = asin.group(0).lower() if asin else f'product-{len(items)+1}'
    if url:
        items.append({'url': url, 'name': name})

matrix = {'include': items}
with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
    f.write(f'matrix={json.dumps(matrix)}\n')
    f.write(f'count={len(items)}\n')

print(f'Parsed {len(items)} product(s):')
for i in items:
    print(f'  [{i["name"]}]  {i["url"]}')
