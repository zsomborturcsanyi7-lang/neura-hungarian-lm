#!/usr/bin/env python3
"""NEURA v3 - Magyar nyelvű hibrid asszisztens rendszer
=================================================
Qwen 2.5 3B (elsődleges, HTTP szerver) + TÖMÖR Logika (gyorsítótár)
"""
import sys, os, json, time, re, subprocess, urllib.request

sys.path.insert(0, 'C:/Users/iga/Desktop/tomor')
from tomor import to_tomor, from_tomor, normalize
from tomor_logic import TomorLogic

REMOTE_SSH = 'ssh -i ~/.ssh/neura_remote_key neura@192.168.0.142'
QWEN_AVAILABLE = False

try:
    r = subprocess.run(f'{REMOTE_SSH} "curl -s http://localhost:18000/"', shell=True, capture_output=True, text=True, timeout=3)
    QWEN_AVAILABLE = (r.returncode == 0 and 'Qwen' in r.stdout)
except:
    pass

def qwen_query(prompt, max_tokens=60, timeout=10):
    """Query Qwen server on remote via SSH."""
    import json as _json, subprocess as _sp
    p = prompt.strip()[:200]
    cmd = f'{REMOTE_SSH} "C:\\Users\\neura\\Python311\\python.exe -u C:\\NeuraNode\\gguf\\qwen_http.py \\"{p}\\" {max_tokens}"'
    try:
        r = _sp.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        resp = _json.loads(r.stdout.strip())['response']
        return resp[:300]
    except:
        pass
    return None

class Neura:
    def __init__(self):
        self.logika = TomorLogic()
        self.memoria = []
        self._init_kb()
        self._tenyt_valasz = {}

    def _init_kb(self):
        """Tudástár TÖMÖR-ben."""
        self._tenyt_valasz = {
            'petofi': 'Petőfi Sándor magyar költő (1823-1849), a magyar romantika kiemelkedő alakja.',
            'petőfi': 'Petőfi Sándor magyar költő (1823-1849), a magyar romantika kiemelkedő alakja.',
            'arany': 'Arany János magyar költő, a Szondi két apródja és a Toldi szerzője.',
            'jokai': 'Jókai Mór magyar író, a nagy magyar regényírók egyike.',
            'jókai': 'Jókai Mór magyar író, a nagy magyar regényírók egyike.',
            '1848': '1848 a magyar forradalom és szabadságharc éve. Március 15-e nemzeti ünnep.',
            'budapest': 'Budapest Magyarország fővárosa, a Duna két partján fekszik.',
            'szechenyi': 'Széchenyi István magyar államférfi, a legnagyobb magyar.',
            'széchenyi': 'Széchenyi István magyar államférfi, a legnagyobb magyar.',
            'kossuth': 'Kossuth Lajos magyar politikus, a szabadságharc vezetője.',
            'magyarorszag': 'Magyarország Közép-Európában található. Területe 93 030 km².',
            'magyarország': 'Magyarország Közép-Európában található. Területe 93 030 km².',
            'balaton': 'A Balaton Magyarország legnagyobb tava, 77 km hosszú.',
            'duna': 'A Duna 2850 km hosszú folyó, keresztülfolyik Magyarországon.',
            'viz': 'A víz kémiai képlete H₂O. 0°C-on fagy, 100°C-on forr.',
            'víz': 'A víz kémiai képlete H₂O. 0°C-on fagy, 100°C-on forr.',
            'fold': 'A Föld a Naprendszer egyik bolygója.',
            'föld': 'A Föld a Naprendszer egyik bolygója.',
            'nap': 'A Nap egy csillag a Tejútrendszerben.',
        }

        for t in [
            "balaton vn 77km hosszu",
            "balaton vn magyarorszagban",
            "duna vn 2850km hosszu",
            "magyarorszag vn europaban",
            "magyarorszag vn 93030km2",
            "budapest vn magyarorszag fovarosa",
            "viz vn h2o",
            "petofi sandor vn magyar kolto",
            "arany janos vn magyar kolto",
            "jokai mor vn magyar iro",
            "1848 vn magyar forradalom",
            "ember vn halando",
            "fold vn bolygo",
            "nap vn csillag",
        ]:
            self.logika.hozzaad_teny(t)
        self.logika.hozzaad_szabaly("?x vn magyarorszagban", "?x vn europaban")

    def ask(self, kerdes):
        t0 = time.time()
        k = kerdes.strip('?.,! ').strip()
        k_norm = normalize(k.lower())

        # === 1. TÖMÖR GYORSÍTÓTÁR ===
        # Regex minták (köszönés, alap)
        valasz = self._direct_match(k_norm)
        if valasz:
            self._save(k, '', valasz)
            return self._result(valasz, t0)

        # Kulcsszó keresés (tények)
        valasz = self._keyword_search(k, k_norm)
        if valasz:
            self._save(k, '', valasz)
            return self._result(valasz, t0)

        # TÖMÖR+Logika
        tomor = to_tomor(k, 'hu')
        logika = self.logika.kerdez(tomor) if len(tomor) > 3 else []
        if logika:
            valasz = from_tomor(logika[0][0], 'hu')
            valasz = self._beautify(valasz, k)
            if valasz:
                self._save(k, tomor, valasz)
                return self._result(valasz, t0, tomor)

        # === 2. QWEN (elsődleges motor) ===
        if QWEN_AVAILABLE:
            valasz = qwen_query(k)
            if valasz and len(valasz) > 3:
                self._save(k, '', valasz)
                return self._result(valasz, t0)

        return self._result('Elnézést, nem tudok válaszolni erre a kérdésre.', t0)

    def _keyword_search(self, k_original, k_norm):
        keywords = [w for w in k_norm.split() if len(w) > 2]
        for kw in keywords:
            for key, valasz in self._tenyt_valasz.items():
                key_norm = normalize(key.lower())
                if key_norm in kw or kw in key_norm:
                    return valasz
        return None

    def _direct_match(self, k_norm):
        minta_valasz = [
            (r'szia|hello|hali|jo napot|jo reggelt|jo estet', 'Üdvözlöm! Miben segíthetek?'),
            (r'kösz|kosz|koszi|koszonom|köszi|köszönöm', 'Szívesen! Továbbra is rendelkezésére állok.'),
            (r'mit tudsz|mit csinalsz|mit tud|miben segitesz|mit tudsz csinalni', 'Magyar nyelvű asszisztens vagyok. Kérdezz bátran!'),
            (r'ki vagy te|ki vagy|mi vagy te|mi vagy|mi a neved|hogy hivnak|hogy hívnak', 'NEURA vagyok, egy magyar nyelvű asszisztens rendszer.'),
            (r'1848|mit tortent 1848|mi tortent 1848', '1848 a magyar forradalom és szabadságharc éve. Március 15-e nemzeti ünnep.'),
            (r'mikor.*marcius|nemzeti unnep|marcus 15', 'Március 15-e a magyar nemzeti ünnep, az 1848-as forradalom emléknapja.'),
        ]
        for minta, valasz in minta_valasz:
            if re.search(minta, k_norm):
                return valasz
        return None

    def _beautify(self, valasz, kerdes):
        if not valasz or valasz == kerdes:
            return None
        valasz = valasz.replace('az ', '').replace('a ', '').strip()
        if valasz.startswith('? '):
            valasz = valasz[2:]
        if len(valasz) < 3:
            return None
        return valasz.capitalize()

    def _save(self, k, t, v):
        self.memoria.append({'ido': time.time(), 'kerdes': k, 'tomor': t, 'valasz': v})
        if len(self.memoria) > 500:
            self.memoria = self.memoria[-250:]

    def _result(self, valasz, t0, tomor=''):
        return {'valasz': valasz, 'ido_ms': f'{(time.time()-t0)*1000:.0f}', 'tomor': tomor}


def main():
    qwen_status = '✅' if QWEN_AVAILABLE else '❌'
    print('╔══════════════════════════════════════════╗')
    print('║       NEURA v3 - Magyar asszisztens     ║')
    print('╠══════════════════════════════════════════╣')
    print(f'║  Qwen 2.5 3B: {qwen_status} (HTTP)                 ║')
    print(f'║  TÖMÖR cache: ✅                       ║')
    print('╚══════════════════════════════════════════╝')
    print()

    n = Neura()
    print('Írj be kérdéseket! (exit = kilépés)')
    print()

    while True:
        try:
            k = input('❯ ').strip()
            if k.lower() in ('exit', 'quit', 'q'):
                break
            if not k:
                continue

            v = n.ask(k)
            print(f'  {v["valasz"]}')
            extra = []
            if v['tomor']:
                extra.append(f'TÖMÖR: {v["tomor"]}')
            extra.append(f'{v["ido_ms"]}ms')
            print(f'  ─ ({" | ".join(extra)})')
            print()

        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            print(f'  Hiba: {e}')

    print('\nViszontlátásra!')

if __name__ == '__main__':
    main()
