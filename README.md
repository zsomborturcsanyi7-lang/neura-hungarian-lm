# NEURA — Hungarian AI Language Model

**A 355M-parameter Hungarian language model** with a custom architecture (GQA + SwiGLU + RMSNorm), trained on an RTX 3070 8GB GPU.

## Model Architecture
- 24 layers, 1024 dimensions, 16 attention heads, 4 KV heads
- SentencePiece 32K tokenizer
- Training data: 2.53B tokens (OpenSubtitles + HunSum-2)
- Best PPL: 48.3 (390K steps)

## Files
| File | Description |
|------|-------------|
| `neura_explorer.py` | Model inspector — forward-pass hooks, neuron activation |
| `neura_forge_v1.pt` | NEURA Forge model (1078 neurons removed/replaced) |
| `neura_monitor.py` | Automatic training monitor + restart |
| `continue_300m.py` | Training continuation script |
| `train_v2.py` | New training script |

## Research Papers
On the Desktop: `neura_research_paper_01-05_*.md`
1. Training Dynamics & Loss Landscape
2. Neuron Specialization & Sparsity
3. Attention Mechanism & Layer Hierarchy
4. Why 355M Can't Reason (& How To Fix It)
5. Practical Guide to Model Editing

## Usage
```bash
# Load model
python neura_explorer.py

# Continue training (RTX 3070)
python continue_300m.py
```

## Dependencies
- PyTorch 2.x + CUDA
- SentencePiece
- NumPy

## Author
Zsombi & Hermes Agent (Nous Research)
