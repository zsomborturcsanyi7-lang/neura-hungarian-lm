#!/usr/bin/env python3
"""Test if 2B BitNet + LoRA fits in 8GB VRAM."""
import torch, time, os
torch._dynamo.config.disable = True
os.environ['TORCHDYNAMO_DISABLE'] = '1'
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model

tok = AutoTokenizer.from_pretrained('microsoft/bitnet-b1.58-2B-4T-bf16', trust_remote_code=True)
tok.pad_token = tok.eos_token

print('Loading BF16 model...', flush=True)
t0 = time.time()
m = AutoModelForCausalLM.from_pretrained(
    'microsoft/bitnet-b1.58-2B-4T-bf16',
    torch_dtype=torch.bfloat16,
    trust_remote_code=False,
    device_map='auto',
)
print(f'  Loaded: {time.time()-t0:.0f}s, VRAM: {torch.cuda.memory_allocated()/1024**3:.1f}GB', flush=True)

for p in m.parameters():
    p.requires_grad = False

cfg = LoraConfig(
    r=16, lora_alpha=32,
    target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj'],
    bias='none', task_type='CAUSAL_LM',
)
m = get_peft_model(m, cfg)
m.print_trainable_parameters()
print(f'LoRA VRAM: {torch.cuda.memory_allocated()/1024**3:.1f}GB', flush=True)
print('OK', flush=True)
