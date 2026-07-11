#!/usr/bin/env python3
"""NEURA Qwen remote query."""
import sys, subprocess, time

REMOTE_SSH = 'ssh -i ~/.ssh/neura_remote_key neura@192.168.0.142'

def query(prompt, timeout=20):
    p = prompt.strip()[:200].replace('"', "'")
    cmd = f'{REMOTE_SSH} "C:\\Users\\neura\\Python311\\python.exe -u C:\\NeuraNode\\gguf\\query_qwen.py \\"{p}\\""'
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
        lines = [l for l in r.stdout.split('\n') if not l.startswith('llama_context') and not l.startswith('llama_model')]
        result = '\n'.join(lines).strip()
        if result:
            return result[:300]
    except:
        pass
    return None

def available():
    try:
        r = subprocess.run(f'{REMOTE_SSH} "echo OK"', shell=True, capture_output=True, text=True, timeout=3)
        return r.returncode == 0 and 'OK' in r.stdout
    except:
        return False

if __name__ == '__main__':
    print('Qwen:', available())
    if len(sys.argv) > 1:
        r = query(' '.join(sys.argv[1:]))
        print('Result:', r)
