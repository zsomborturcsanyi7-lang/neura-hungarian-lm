#!/usr/bin/env python3
"""Test the 2B BitNet with Hungarian prompts."""
import torch, os, time
torch._dynamo.config.disable = True
os.environ['TORCHDYNAMO_DISABLE'] = '1'
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig

print('Loading...', flush=True)
tok = AutoTokenizer.from_pretrained('microsoft/bitnet-b1.58-2B-4T', trust_remote_code=True)
cfg = AutoConfig.from_pretrained('microsoft/bitnet-b1.58-2B-4T', trust_remote_code=False)
m = AutoModelForCausalLM.from_pretrained('microsoft/bitnet-b1.58-2B-4T', config=cfg, torch_dtype='auto', trust_remote_code=False, device_map='auto')

print('Testing Hungarian...', flush=True)
prompts = [
    'Mi a magyar fovaros?',
    'Meselj a Balatonrol!',
    'Mi az ELTE?',
    'Irj egy rovid verset a naplementerol!',
]
for p in prompts:
    t0 = time.time()
    msgs = [{'role': 'user', 'content': p}]
    prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    inputs = tok(prompt, return_tensors='pt').to(m.device)
    outputs = m.generate(**inputs, max_new_tokens=40)
    r = tok.decode(outputs[0][inputs['input_ids'].shape[-1]:], skip_special_tokens=True)
    print(f'  [{time.time()-t0:.1f}s] {p} -> {r}', flush=True)
print('DONE', flush=True)
