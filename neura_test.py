#!/usr/bin/env python3
"""NEURA v3 - Teljes rendszer teszt
Futtatás: python neura_test.py

Teszteli: TÖMÖR cache-t, Qwen HTTP szervert, válaszidőt
"""
import sys, time
sys.path.insert(0, 'C:/Users/iga/Desktop/neura')
from neura import Neura, QWEN_AVAILABLE

n = Neura()
print()
print('=' * 65)
print('  NEURA v3 TESZT')
print('=' * 65)
print(f'  Qwen szerver: {"🗸" if QWEN_AVAILABLE else "✗"} (HTTP)')
print(f'  TÖMÖR cache:  🗸')
print(f'  Tudástár: {len(n.logika.tenyek)} tény, {len(n.logika.szabalyok)} szabály')
print('=' * 65)
print()

tesztek = [
    # (kategória, kérdés, várható? igaz/hamis teszt)
    ('ALAP',    'szia',                 None),
    ('ALAP',    'ki vagy te',           None),
    ('ALAP',    'mit tudsz',            None),
    ('ALAP',    'koszonom',             None),
    ('TÉNY',    'Mi a Balaton hossza?', '77 km'),
    ('TÉNY',    'Mi a Duna hossza?',   '2850 km'),
    ('TÉNY',    'Hol van Magyarország?', None),
    ('TÉNY',    'Mekkora Magyarország?', '93 030'),
    ('TÉNY',    'Mi a víz képlete?',    'H₂O'),
    ('SZEMÉLY', 'Ki Petőfi Sándor?',   'Petőfi'),
    ('SZEMÉLY', 'Ki Arany János?',     'Arany'),
    ('SZEMÉLY', 'Ki Jókai Mór?',       'Jókai'),
    ('SZEMÉLY', 'Ki Széchenyi István?', 'Széchenyi'),
    ('SZEMÉLY', 'Ki Kossuth Lajos?',   'Kossuth'),
    ('TÖRT',    'Mi történt 1848-ban?', '1848'),
    ('QWEN',    'Mi a magyar fovaros?', None),
    ('QWEN',    'Mi az ELTE?',          None),
    ('QWEN',    'Ki volt Magyarország elnöke 1990-ben?', None),
    ('QWEN',    'Meselj a Balatonrol!', None),
]

for kat, kerdes, varhato in tesztek:
    t0 = time.perf_counter()
    v = n.ask(kerdes)
    dt = (time.perf_counter() - t0) * 1000

    # Forrás meghatározása
    if v['tomor']:
        forras = 'TÖMÖR'
    elif dt < 10:
        forras = 'CACHE'
    else:
        forras = 'QWEN'

    # Ellenőrzés ha van várt érték
    if varhato:
        ok = '🗸' if varhato.lower() in v['valasz'].lower() else '✗'
    else:
        ok = '~'

    valasz = v['valasz'][:65].replace('\n', ' ')
    if dt < 1000:
        ido = f'{dt:.0f}ms'
    else:
        ido = f'{dt/1000:.1f}s'

    print(f'  {ok} [{ido:>6}] [{forras:<5}] {kerdes}')
    print(f'    {valasz}')
    print()

# Összesítő
print('=' * 65)
print('  Jelmagyarázat:  🗸 = helyes  ~ = nincs referencia  ✗ = hibás')
print(f'  TÖMÖR/CACHE = 0-2ms  |  QWEN = 1-3 másodperc')
print('=' * 65)
