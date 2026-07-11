#!/usr/bin/env python3
"""Quick test: load SFT model and generate a response."""
import sys, os, torch, time
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
sys.path.insert(0, 'C:/NeuraNode/bitnet')
from pulse_350m_bitnet import Pulse350M_BitNet
import sentencepiece as spm

sp = spm.SentencePieceProcessor()
sp.Load('C:/NeuraNode/bitnet/bitnet_kaggle_data/tokenizer.model')

ckpt = torch.load('C:/NeuraNode/bitnet/checkpoints/sft/best_sft.pt', map_location='cpu', weights_only=True)
model = Pulse350M_BitNet(32000, 1024, 16, 4, 24, 8192)
model.load_state_dict(ckpt['model_state'], strict=False)
model.eval().cuda()
print(f'Loaded: SFT step {ckpt.get("sft_step","?")}, loss {ckpt.get("loss","?"):.4f}', flush=True)

# Test 1: simple forward pass
print('Test 1: forward pass...', flush=True)
x = torch.randint(0, 1000, (1, 16)).cuda()
with torch.no_grad():
    y = model(x)
    print(f'  Output shape: {y.shape}', flush=True)

# Test 2: generate
print('Test 2: generate...', flush=True)
prompt = '### Utasítás: Mi a magyar főváros?\n### Válasz:'
ids = sp.Encode(prompt, out_type=int)
x = torch.tensor([ids]).cuda()
print(f'  Input: {len(ids)} tokens', flush=True)

t0 = time.time()
with torch.no_grad():
    for i in range(30):
        y = model(x)
        nid = torch.argmax(y[0, -1, :]).item()
        if nid == 2:  # </s>
            break
        x = torch.cat([x, torch.tensor([[nid]]).cuda()], dim=1)

print(f'  Time: {time.time()-t0:.1f}s, {x.shape[1]-len(ids)} tokens generated', flush=True)
print(f'  Output: {sp.Decode(x[0].tolist())}', flush=True)
print('DONE', flush=True)
