# NEURA 300M — 355M Parameter Hungarian Language Model

**Status:** ✅ Working — model trained, text generation tested at 390K steps (PPL=48.3)

355M parameter Hungarian language model with custom architecture (GQA + SwiGLU + RMSNorm), trained on an RTX 3070 8GB GPU.

## ⚠️ THIS PROJECT IS UNFINISHED — FEEL FREE TO CONTINUE IT ⚠️

This project was developed by Zsombi & Hermes Agent (Nous Research).

---

## Architecture
- 24 layers, 1024 dimensions, 16 attention heads, 4 KV heads
- SentencePiece 32K tokenizer
- Training data: 2.53B tokens (OpenSubtitles + HunSum-2)
- Best PPL: 48.3 (390K steps)

## Files
| File | Description |
|------|-------------|
| `neura.py` | Model architecture |
| `sft_train.py` | SFT training |
| `test_neura.py` | Testing |
| `deploy_sft.py` | Deployment |

## Developer
Zsombi & Hermes Agent (Nous Research)
