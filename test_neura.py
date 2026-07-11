#!/usr/bin/env python3
"""Test the full NEURA pipeline components."""
import torch, os, time
torch._dynamo.config.disable = True
os.environ['TORCHDYNAMO_DISABLE'] = '1'
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig
import sentencepiece as spm

# ========== 1. Load 2B BitNet ==========
print('=== NEURA Test ===', flush=True)
print('\n[1] Loading 2B BitNet (creative layer)...', flush=True)
t0 = time.time()
tok = AutoTokenizer.from_pretrained('microsoft/bitnet-b1.58-2B-4T', trust_remote_code=True)
cfg = AutoConfig.from_pretrained('microsoft/bitnet-b1.58-2B-4T', trust_remote_code=False)
model_2b = AutoModelForCausalLM.from_pretrained(
    'microsoft/bitnet-b1.58-2B-4T', config=cfg,
    torch_dtype='auto', trust_remote_code=False, device_map='auto',
)
print(f'  2B BitNet: {time.time()-t0:.0f}s, {sum(p.numel() for p in model_2b.parameters())/1e6:.0f}M params', flush=True)

# ========== 2. Test English generation ==========
print('\n[2] Testing English generation...', flush=True)
prompts = [
    'What is the capital of Hungary?',
    'Write a short poem about the sunset.',
    'What is the meaning of life?',
]
for p in prompts:
    t = time.time()
    msgs = [{'role': 'user', 'content': p}]
    prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    inputs = tok(prompt, return_tensors='pt').to(model_2b.device)
    outputs = model_2b.generate(**inputs, max_new_tokens=40)
    r = tok.decode(outputs[0][inputs['input_ids'].shape[-1]:], skip_special_tokens=True)
    print(f'  [{time.time()-t:.1f}s] {p}', flush=True)
    print(f'    -> {r}', flush=True)

# ========== 3. Test IdentNet 330M ==========
print('\n[3] Loading IdentNet 330M (intent detection)...', flush=True)
t0 = time.time()
sys_path_backup = list(__import__('sys').path)
import sys
sys.path.insert(0, 'C:/NeuraNode/bitnet')
from pulse_350m_bitnet import Pulse350M_BitNet
sp = spm.SentencePieceProcessor()
sp.Load('C:/NeuraNode/bitnet/bitnet_kaggle_data/tokenizer.model')
ckpt = torch.load('C:/NeuraNode/bitnet/checkpoints/sft/best_sft.pt', map_location='cpu', weights_only=True)
identnet = Pulse350M_BitNet(32000, 1024, 16, 4, 24, 8192)
identnet.load_state_dict(ckpt['model_state'], strict=False)
identnet.eval().cuda()
print(f'  IdentNet: {time.time()-t0:.0f}s, loss={ckpt.get("loss",0):.4f}', flush=True)

# Test IdentNet on Hungarian prompts
hu_prompts = [
    'Mi a magyar fovaros?',
    'Hogyan keszul a rantotta?',
    'Meselj a Balatonrol!',
]
print('\n[4] Testing IdentNet (perplexity on Hungarian)...', flush=True)
for p in hu_prompts:
    t = time.time()
    prefix = '### Utasitas: ' + p + '\n### Valasz:'
    ids = sp.Encode(prefix, out_type=int)
    x = torch.tensor([ids[:-1]]).cuda()
    y = torch.tensor([ids[1:]]).cuda().long()
    with torch.no_grad():
        out = identnet(x)
        loss = torch.nn.functional.cross_entropy(out.view(-1, out.size(-1)), y.view(-1))
    print(f'  [{time.time()-t:.2f}s] ppl={torch.exp(loss).item():.1f} loss={loss.item():.3f}', flush=True)
    print(f'    Input: {p}', flush=True)

print('\n=== DONE ===', flush=True)
