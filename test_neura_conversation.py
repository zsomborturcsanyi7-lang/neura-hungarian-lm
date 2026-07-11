#!/usr/bin/env python3
"""NEURA használhatósági és kommunikációs teszt"""
import sys, time
sys.path.insert(0, 'C:/Users/iga/Desktop/neura')
sys.path.insert(0, 'C:/Users/iga/Desktop/tomor')
from neura import Neura, BITNET_AVAILABLE

n = Neura()

def teszt_kerdes(kerdes, szoveg):
    t0 = time.perf_counter()
    v = n.ask(kerdes)
    dt = (time.perf_counter() - t0) * 1000
    tomor_info = 'TÖMÖR: %s' % v['tomor'] if v['tomor'] else ''
    print('  ❯ %s' % kerdes)
    print('  ← %s' % v['valasz'])
    if tomor_info:
        print('    (%s, %.0fms)' % (tomor_info, float(v['ido_ms'])))
    else:
        print('    (%.0fms)' % float(v['ido_ms']))
    print()

print('=' * 60)
print('  NEURA HASZNÁLÁTHATÓSÁGI TESZT')
print('  BitNet elérhető: %s' % ('✅' if BITNET_AVAILABLE else '❌'))
print('=' * 60)

# === BESZÉLGETÉS 1: Alap kérdések ===
print('\n--- BESZÉLGETÉS 1: Alap kérdések ---\n')

teszt_kerdes('Szia!', 'Köszönés')
teszt_kerdes('Hogy hívnak?', 'Név')
teszt_kerdes('Mit tudsz csinálni?', 'Képesség')
teszt_kerdes('Köszönöm a segítséget!', 'Köszönet')

# === BESZÉLGETÉS 2: Tények ===
print('--- BESZÉLGETÉS 2: Tények ---\n')

teszt_kerdes('Mennyi a Balaton hossza?', 'Tény')
teszt_kerdes('Hol található a Balaton?', 'Tény')
teszt_kerdes('Mekkora Magyarország területe?', 'Tény')
teszt_kerdes('Mi a Duna hossza?', 'Tény')
teszt_kerdes('Mi a víz képlete?', 'Tény')

# === BESZÉLGETÉS 3: Személyek ===
print('--- BESZÉLGETÉS 3: Személyek ---\n')

teszt_kerdes('Ki Petőfi Sándor?', 'Személy')
teszt_kerdes('Ki Arany János?', 'Személy')
teszt_kerdes('Ki Jókai Mór?', 'Személy')
teszt_kerdes('Ki Széchenyi István?', 'Személy')

# === BESZÉLGETÉS 4: Történelem ===
print('--- BESZÉLGETÉS 4: Történelem ---\n')

teszt_kerdes('Mi történt 1848-ban?', 'Történelem')
teszt_kerdes('Mikor van a nemzeti ünnep?', 'Történelem')

# === BESZÉLGETÉS 5: Memória ===
print('--- BESZÉLGETÉS 5: Memória ---\n')

teszt_kerdes('Ki Petőfi Sándor?', 'Előzmény')
teszt_kerdes('Emlékszel, mit kérdeztem az előbb?', 'Memória')

# === BESZÉLGETÉS 6: Ismeretlen témák ===
print('--- BESZÉLGETÉS 6: Ismeretlen témák ---\n')

teszt_kerdes('Mi az ELTE?', 'Ismeretlen')
teszt_kerdes('Hogyan kell palacsintát sütni?', 'Ismeretlen')
teszt_kerdes('Mi a kvantummechanika?', 'Ismeretlen')
teszt_kerdes('Mesélj a Marsról!', 'Ismeretlen')

# === BESZÉLGETÉS 7: Több lépéses ===
print('--- BESZÉLGETÉS 7: Több lépéses ---\n')

teszt_kerdes('Ismered a Balatont?', 'Több lépés')
teszt_kerdes('Hol van?', 'Több lépés - kontextus nélkül')

# === BESZÉLGETÉS 8: Nyelvi változatok ===
print('--- BESZÉLGETÉS 8: Nyelvi változatok ---\n')

teszt_kerdes('Szia!', 'Köszönés')
teszt_kerdes('Helló!', 'Köszönés 2')
teszt_kerdes('Hi!', 'Köszönés 3')

# === EREDMÉNY ===
print('=' * 60)
print('  EREDMÉNYEK')
print('=' * 60)

sikeres = 0
osszes = 0
for kategoria, kerdesek, elvart in [
    ('Alap', ['szia', 'hogy hívnak', 'mit tudsz', 'köszönöm'],
     ['Üdvözlöm', 'NEURA', 'Magyar nyelvű', 'Szívesen']),
    ('Tények', ['balaton hossza', 'balaton hol', 'magyarország területe', 'duna hossza', 'víz képlete'],
     ['77 km', 'Balaton', '93 030', '2850', 'H2O']),
    ('Személyek', ['petőfi', 'arany', 'jókai', 'széchenyi'],
     ['Petőfi', 'Arany', 'Jókai', 'Széchenyi']),
    ('Ismeretlen', ['ELTE', 'palacsintát', 'kvantummechanika', 'Marsról'],
     ['Elnézést']),
]:
    print('\n  %s:' % kategoria)
    print('  ' + '-' * 40)
    for k, e in zip(kerdesek, elvart):
        osszes += 1
        v = n.ask(k)
        siker = any(evo.lower() in v['valasz'].lower() for evo in e.split('|'))
        if siker:
            sikeres += 1
        print('  %s %-30s → %s' % ('✅' if siker else '❌', k[:28], v['valasz'][:35]))

print('\n  ÖSSZESEN: %d/%d sikeres (%.0f%%)' % (sikeres, osszes, sikeres/osszes*100 if osszes else 0))
print('\n  TÖMÖR használat a logikában: %d/%d alkalommal' % (
    sum(1 for e in n.memoria if e['tomor']), len(n.memoria)))
print('=' * 60)
