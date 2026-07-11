#!/usr/bin/env python3
"""
BitNet 2B Hungarian SFT with LoRA.
Uses QLoRA-style: BF16 model frozen, LoRA adapters on attention.
Trains on alpaca-cleaned-gemini-hun (Hungarian instruction dataset).
"""
import os, sys, torch, time
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
os.environ['TORCHDYNAMO_DISABLE'] = '1'
torch._dynamo.config.disable = True

from transformers import (
    AutoTokenizer, AutoModelForCausalLM, AutoConfig,
    TrainingArguments, BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
from datasets import load_dataset
import gc

MODEL_ID = 'microsoft/bitnet-b1.58-2B-4T-bf16'
SAVE_DIR = 'C:/NeuraNode/bitnet/checkpoints/bitnet2b_sft'
LORA_R = 16
LORA_ALPHA = 32
LR = 3e-4
EPOCHS = 1
MAX_SEQ_LEN = 256
BATCH_SIZE = 1
GRAD_ACCUM = 4
USE_8BIT = True  # 8-bit Adam to save VRAM

print('=== BitNet 2B Hungarian SFT ===')
print(f'LoRA rank={LORA_R}, LR={LR}, Epochs={EPOCHS}')

# 1. TOKENIZER
print('\n[1] Loading tokenizer...', flush=True)
tok = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
tok.pad_token = tok.eos_token

# 2. DATASET
print('\n[2] Loading Hungarian SFT data...', flush=True)
ds = load_dataset('Bazsalanszky/alpaca-cleaned-gemini-hun', split='train')
ds = ds.select(range(5000))  # subset for speed

def format_chat(example):
    msgs = []
    if example['input'] and len(example['input'].strip()) > 0:
        content = example['instruction'] + '\n' + example['input']
    else:
        content = example['instruction']
    msgs.append({'role': 'user', 'content': content})
    msgs.append({'role': 'assistant', 'content': example['response']})
    text = tok.apply_chat_template(msgs, tokenize=False)
    return {'text': text}

ds = ds.map(format_chat, remove_columns=ds.column_names)
print(f'  Samples: {len(ds)}')
print(f'  Sample: {ds[0]["text"][:100]}...', flush=True)

# 3. MODEL with LoRA
print('\n[3] Loading model with LoRA...', flush=True)
t0 = time.time()

# Load BF16 model (full precision for fine-tuning)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.bfloat16,
    trust_remote_code=False,
    device_map='auto',
    use_cache=False,  # required for gradient checkpointing
)

# Use 8-bit Adam to reduce memory
import torch.optim as optim_module
if USE_8BIT:
    try:
        import bitsandbytes as bnb
        optimizer = 'adamw_bnb_8bit'
        print('  8-bit Adam enabled', flush=True)
    except ImportError:
        optimizer = 'adamw_torch'
        print('  bitsandbytes not available, using standard AdamW', flush=True)
else:
    optimizer = 'adamw_torch'
print(f'  Loaded: {time.time()-t0:.0f}s', flush=True)
print(f'  VRAM: {torch.cuda.memory_allocated()/1024**3:.1f}GB', flush=True)

# Freeze all base model parameters
for param in model.parameters():
    param.requires_grad = False

# LoRA config - target attention layers (BitNet uses standard attention modules)
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    lora_dropout=0.05,
    target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj'],  # standard attention
    bias='none',
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
print(f'  VRAM after LoRA: {torch.cuda.memory_allocated()/1024**3:.1f}GB', flush=True)

# Memory cleanup
gc.collect()
torch.cuda.empty_cache()

# 4. TRAINING ARGUMENTS
print('\n[4] Setting up training...', flush=True)
args = TrainingArguments(
    output_dir=SAVE_DIR,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRAD_ACCUM,
    num_train_epochs=EPOCHS,
    learning_rate=LR,
    fp16=False,
    bf16=True,
    optim=optimizer,
    logging_steps=10,
    save_steps=500,
    save_total_limit=3,
    remove_unused_columns=True,
    report_to='none',
    dataloader_num_workers=0,
    gradient_checkpointing=True,
)

from trl import SFTTrainer
trainer = SFTTrainer(
    model=model,
    processing_class=tok,
    args=args,
    train_dataset=ds,
)

# 5. TRAIN
print('\n[5] Training...', flush=True)
trainer.train()

# Save LoRA adapters
print('\n[6] Saving...', flush=True)
model.save_pretrained(f'{SAVE_DIR}/lora_adapter')
tok.save_pretrained(f'{SAVE_DIR}/lora_adapter')
print(f'  Saved to: {SAVE_DIR}/lora_adapter', flush=True)
print('DONE', flush=True)
