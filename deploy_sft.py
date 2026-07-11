import subprocess, base64

# Read the SFT script
with open('C:/Users/iga/Desktop/neura/sft_train.py', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()

# PowerShell command to decode and write
ps_cmd = f'$b64="{b64}";$bytes=[System.Convert]::FromBase64String($b64);[System.IO.File]::WriteAllBytes(\'C:\\NeuraNode\\bitnet\\sft_train.py\',$bytes);Write-Host "OK $($bytes.Length) bytes"'

# Run via SSH
cmd = ['ssh', '-i', '~/.ssh/neura_remote_key', 'neura@192.168.0.142', f'powershell -Command "{ps_cmd}"']
r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
print(r.stdout)
if r.stderr:
    print('STDERR:', r.stderr[:500])
print('EXIT:', r.returncode)
