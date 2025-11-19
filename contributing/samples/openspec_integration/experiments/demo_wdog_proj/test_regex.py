#!/usr/bin/env python3
import re

with open('wdt.md', 'r', encoding='utf-8') as f:
    content = f.read()
    
pattern = r'(?:\*\*|#{2,4}\s*)([A-Z][\w\s]+?)\s+register\s+\[0x([0-9A-Fa-f]+)\]'
matches = list(re.finditer(pattern, content, re.IGNORECASE))

print(f'Found {len(matches)} matches')
for m in matches[:12]:
    print(f'  - {m.group(1).strip()} @ 0x{m.group(2)}')
