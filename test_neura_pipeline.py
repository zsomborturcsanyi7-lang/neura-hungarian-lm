#!/usr/bin/env python3
"""NEURA pipeline teszt - minden komponens"""
import sys, os, time, json

# TÖMÖR
sys.path.insert(0, 'C:/Users/iga/Desktop/tomor')
from tomor import to_tomor, from_tomor
from tomor_logic import TomorLogic

print('=' * 60)
print('  NEURA PIPELINE TESZT')
print('=' * 60)

# === 1. TÖMÖR FORDÍTÁS TESZT ===
print('\n--- 1. TÖMÖR fordítás ---')
tesztek = [
    ('hu', 'Szia hogy vagy'),
    ('hu', 'Hol van Budapest'),
    ('hu', 'Mi a Balaton hossza'),
    ('hu', 'Ki Petőfi Sándor'),
    ('hu', 'Mekkora Magyarország'),
    ('en', 'What is the capital of France'),
    ('en', 'How long is the Danube'),
]
for lang, text in tesztek:
    t0 = time.perf_counter()
    tomor = to_tomor(text, lang)
    vissza = from_tomor(tomor, lang)
    dt = (time.perf_counter() - t0) * 1000
    print('  %-40s -> TÖMÖR: %-20s -> %s  [%.1fms]' % (text, tomor, vissza, dt))

# === 2. LOGIKAI MOTOR TESZT ===
print('\n--- 2. Logikai motor ---')
l = TomorLogic()
for t in [
    "balaton vn 77km hosszu",
    "balaton vn magyarorszagban",
    "duna vn 2850km hosszu",
    "magyarorszag vn europaban",
    "ember vn halando",
    "fold vn bolygo",
    "nap vn csillag",
    "viz vn h2o",
    "petofi sandor vn magyar kolto",
    "budapest vn magyarorszag fovarosa",
]:
    l.hozzaad_teny(t)
l.hozzaad_szabaly("?x vn magyarorszagban", "?x vn europaban")

kerdesek = [
    "? vn 77km hosszu",
    "? vn europaban",
    "? vn magyarorszagban",
    "? vn magyar kolto",
    "? vn bolygo",
]
for k in kerdesek:
    t0 = time.perf_counter()
    valaszok = l.kerdez(k)
    dt = (time.perf_counter() - t0) * 1000
    for v, m in valaszok:
        print('  %-30s -> %-25s (%d lépés) [%.2fms]' % (k, v, m, dt))

# === 3. TELJES NEURA PIPELINE ===
print('\n--- 3. Teljes NEURA pipeline (TÖMÖR+Logika+Kulcsszó) ---')
sys.path.insert(0, 'C:/Users/iga/Desktop/neura')
from neura import Neura

n = Neura()

kerdesek = [
    'Szia!',
    'Mi a neved?',
    'Mit tudsz?',
    'Mi a Balaton hossza?',
    'Hol van Magyarország?',
    'Ki Petőfi Sándor?',
    'Mi Budapest?',
    'Mekkora Magyarország?',
    'Mi a víz képlete?',
    'Köszönöm!',
]

print('  %-40s %-30s %s' % ('Kérdés', 'Válasz', 'Idő'))
print('  ' + '-' * 90)
for k in kerdesek:
    t0 = time.perf_counter()
    v = n.ask(k)
    dt = (time.perf_counter() - t0) * 1000
    extra = 'TÖMÖR' if v['tomor'] else 'Kulcsszó/Minta'
    print('  %-40s %-30s %6.0fms [%s]' % (k, v['valasz'][:28], float(v['ido_ms']), extra))

# === 4. SEBESSÉG TESZT ===
print('\n--- 4. Sebesség teszt (20 gyors kérdés) ---')
gyors_kerdesek = ['Szia!', 'Mi a Balaton hossza?', 'Hol van Budapest?', 'Ki Petőfi?', 'Köszönöm!'] * 4

t0 = time.perf_counter()
for k in gyors_kerdesek:
    n.ask(k)
dt = (time.perf_counter() - t0) * 1000
print('  %d kérdés: %.0fms összesen, %.1fms/kérdés' % (len(gyors_kerdesek), dt, dt/len(gyors_kerdesek)))

# === 5. MEMÓRIA TESZT ===
print('\n--- 5. Memória teszt ---')
n.ask('Ki Petőfi Sándor?')
n.ask('Emlékszel rá?')
# Nézzük mit tárol
print('  Memória mérete: %d bejegyzés' % len(n.memoria))
if n.memoria:
    utolso = n.memoria[-1]
    print('  Utolsó: "%s" -> "%s"' % (utolso['kerdes'], utolso['valasz']))

print('\n' + '=' * 60)
print('  TESZT VÉGE')
print('=' * 60)
