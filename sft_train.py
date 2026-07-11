#!/usr/bin/env python3
"""
Pulse 330M SFT - Instruction fine-tuning on Hungarian SFT data.
Trains from rlaif/best.pt on alpaca-cleaned-gemini-hun dataset.
Fixed: SFT-specific loss tracking, moving avg for stable checkpointing.
"""
import sys, os, torch, time, math
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
sys.path.insert(0, 'C:/NeuraNode/bitnet')
from pulse_350m_bitnet import Pulse350M_BitNet
import sentencepiece as spm

# ===== CONFIG =====
CKPT_PATH = 'C:/NeuraNode/bitnet/checkpoints/rlaif/best.pt'
SAVE_DIR = 'C:/NeuraNode/bitnet/checkpoints/sft'
TOKENIZER='C:/NeuraNode/bitnet/bitnet_kaggle_data/tokenizer.model'
LR = 2e-5
STEPS = 10000
LOG_EVERY = 100
SAVE_EVERY = 1000
AVG_WINDOW = 50   # moving average over N steps for loss comparison
SEQ_LEN = 512

print('=== Pulse 330M SFT on Hungarian Instruction Data ===')
print(f'Steps: {STEPS}, LR: {LR}, AvgWindow: {AVG_WINDOW}')

# ===== 1. LOAD TOKENIZER =====
print('\n[1/6] Loading tokenizer...')
sp = spm.SentencePieceProcessor()
sp.Load(TOKENIZER)
print(f'  Vocab: {sp.GetPieceSize()}')

# ===== 2. LOAD DATASET =====
print('\n[2/6] Loading SFT dataset...')
from datasets import load_dataset
ds = load_dataset('Bazsalanszky/alpaca-cleaned-gemini-hun', split='train')
print(f'  Dataset: {len(ds)} samples')

# ===== 3. FORMAT & TOKENIZE =====
print('\n[3/6] Formatting and tokenizing...')
def format_sample(sample):
    """Convert to our instruction format."""
    parts = []
    parts.append(f"### Utasítás: {sample['instruction']}")
    if sample['input'] and len(sample['input'].strip()) > 0:
        parts.append(f"### Bemenet: {sample['input']}")
    parts.append(f"### Válasz: {sample['response']}")
    return '\n'.join(parts)

all_tokens = []
skipped = 0
for i, sample in enumerate(ds):
    text = format_sample(sample)
    ids = sp.Encode(text, out_type=int)
    if len(ids) < 10:
        skipped += 1
        continue
    if len(ids) > SEQ_LEN:
        ids = ids[:SEQ_LEN]
    all_tokens.append(torch.tensor(ids, dtype=torch.long))
    if (i + 1) % 10000 == 0:
        print(f'  Tokenized {i+1}/{len(ds)}')

print(f'  Tokenized: {len(all_tokens)} sequences, skipped: {skipped}')
os.makedirs(SAVE_DIR, exist_ok=True)
torch.save(all_tokens, f'{SAVE_DIR}/sft_data.pt')
print(f'  Saved: {SAVE_DIR}/sft_data.pt')

# ===== 4. LOAD MODEL =====
print('\n[4/6] Loading model...')
ckpt = torch.load(CKPT_PATH, map_location='cpu', weights_only=True)
model = Pulse350M_BitNet(32000, 1024, 16, 4, 24, 8192)
model.load_state_dict(ckpt['model_state'], strict=False)
model.train().cuda()
start_loss = ckpt.get('loss', 0)
start_step = ckpt.get('steps', 200000)
print(f'  RLAIF ckpt: loss {start_loss:.4f} at step {start_step}')
stats = model.count_params()
print(f'  {stats["total_m"]}M params, ~{stats["bitnet_mb"]}MB BitNet')

# ===== 5. SETUP OPTIMIZER =====
print('\n[5/6] Setting up optimizer...')
opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=0.01)
print(f'  AdamW, LR={LR}')

# ===== 6. TRAINING =====
print('\n[6/6] Training...')
print('=' * 60)

# SFT-specific best loss (starts from inf, NOT from RLAIF loss)
best_sft_loss = float('inf')
loss_history = []  # for moving average
t0 = time.time()
total_tokens = 0
last_avg_loss = 999

for step in range(STEPS):
    idx = torch.randint(0, len(all_tokens), (1,)).item()
    tokens = all_tokens[idx]
    
    x = tokens[:-1].unsqueeze(0).cuda()
    y = tokens[1:].unsqueeze(0).cuda().long()
    
    out = model(x)
    loss = torch.nn.functional.cross_entropy(out.view(-1, out.size(-1)), y.view(-1))
    
    opt.zero_grad()
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    opt.step()
    
    total_tokens += x.numel()
    loss_history.append(loss.item())
    
    # Keep window size
    if len(loss_history) > AVG_WINDOW:
        loss_history.pop(0)
    
    if (step + 1) % LOG_EVERY == 0:
        avg_loss = sum(loss_history) / len(loss_history)
        last_avg_loss = avg_loss
        elapsed = time.time() - t0
        tok_s = total_tokens / max(1, elapsed)
        print(f'  [{step+1}/{STEPS}] loss: {loss.item():.4f} | avg{AVG_WINDOW}: {avg_loss:.4f} | best_sft: {best_sft_loss:.4f} | {elapsed:.0f}s | {tok_s:.0f} tok/s', flush=True)
        
        # Save if moving average beats SFT best
        if avg_loss < best_sft_loss and avg_loss > 0:
            best_sft_loss = avg_loss
            torch.save({
                'model_state': model.state_dict(),
                'steps': start_step + step + 1,
                'loss': avg_loss,
                'type': 'sft',
                'sft_step': step + 1,
            }, f'{SAVE_DIR}/best_sft.pt')
            print(f'  *** NEW SFT BEST: {best_sft_loss:.4f} (avg over {AVG_WINDOW}) ***', flush=True)
    
    if (step + 1) % SAVE_EVERY == 0:
        torch.save({
            'model_state': model.state_dict(),
            'steps': start_step + step + 1,
            'loss': loss.item(),
            'type': 'sft',
            'sft_step': step + 1,
        }, f'{SAVE_DIR}/checkpoint_{step+1}.pt')
        print(f'  Checkpoint saved at step {step+1}', flush=True)

# Final save
torch.save({
    'model_state': model.state_dict(),
    'steps': start_step + STEPS,
    'loss': last_avg_loss,
    'type': 'sft',
    'sft_step': STEPS,
}, f'{SAVE_DIR}/final.pt')

elapsed = time.time() - t0
print(f'\n[DONE] Best SFT loss: {best_sft_loss:.4f}')
print(f'Time: {elapsed:.0f}s ({elapsed/60:.1f}min)')
print(f'Tokens processed: {total_tokens:,}')
