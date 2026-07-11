#!/usr/bin/env python3
"""Compare RLAIF vs SFT model generation."""
import sys, os, torch, time
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
sys.path.insert(0, 'C:/NeuraNode/bitnet')
from pulse_350m_bitnet import Pulse350M_BitNet
import sentencepiece as spm

sp = spm.SentencePieceProcessor()
sp.Load('C:/NeuraNode/bitnet/bitnet_kaggle_data/tokenizer.model')

def load_model(path):
    ckpt = torch.load(path, map_location='cpu', weights_only=True)
    model = Pulse350M_BitNet(32000, 1024, 16, 4, 24, 8192)
    model.load_state_dict(ckpt['model_state'], strict=False)
    model.eval().cuda()
    return model, ckpt.get('loss', 0), ckpt.get('steps', ckpt.get('sft_step', 0))

def generate(model, prompt, max_tokens=40, temp=0.8):
    ids = sp.Encode(prompt, out_type=int)
    x = torch.tensor([ids]).cuda()
    with torch.no_grad():
        for i in range(max_tokens):
            y = model(x)
            logits = y[0, -1, :] / temp
            probs = torch.softmax(logits, dim=-1)
            nid = torch.multinomial(probs, 1).item()
            if nid == 2:  # </s>
                break
            x = torch.cat([x, torch.tensor([[nid]]).cuda()], dim=1)
    return sp.Decode(x[0].tolist())

# Load both models
print('Loading RLAIF model...', flush=True)
rlaif, rl_loss, rl_step = load_model('C:/NeuraNode/bitnet/checkpoints/rlaif/best.pt')
print(f'  Loss: {rl_loss:.4f} @ step {rl_step}', flush=True)

print('Loading SFT model...', flush=True)
sft, sft_loss, sft_step = load_model('C:/NeuraNode/bitnet/checkpoints/sft/best_sft.pt')
print(f'  Loss: {sft_loss:.4f} @ step {sft_step}', flush=True)

# Test prompts
prompts = [
    '### Utasítás: Mi a magyar főváros?\n### Válasz:',
    '### Utasítás: Hogyan készítsünk rántottát?\n### Válasz:',
]

for model_name, model, loss, step in [('RLAIF', rlaif, rl_loss, rl_step), ('SFT', sft, sft_loss, sft_step)]:
    print(f'\n{"="*50}', flush=True)
    print(f'{model_name} (loss={loss:.4f}, step={step})', flush=True)
    for prompt in prompts:
        print(f'\n  Prompt: {prompt[:60]}...', flush=True)
        t0 = time.time()
        out = generate(model, prompt, max_tokens=40, temp=0.8)
        print(f'  [{time.time()-t0:.1f}s] {out}', flush=True)

print('\nDONE', flush=True)
