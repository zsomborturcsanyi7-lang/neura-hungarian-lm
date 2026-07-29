# neura-hungarian-lm

Training code and architecture configuration for a 355M parameter Hungarian Transformer language model.

## Overview & Purpose
neura-hungarian-lm provides an open pipeline for pretraining a 355M parameter decoder-only Transformer model using Grouped Query Attention (GQA) and SwiGLU activations on Hungarian text datasets.

## Key Features
- 355M parameter Transformer architecture (GQA + SwiGLU + RMSNorm).
- Custom tokenizer training scripts.
- Perplexity evaluation routines.

## Tech Stack & Dependencies
- **Framework**: PyTorch
- **Libraries**: HuggingFace Transformers, Tokenizers
- **Language**: Python 3.10+

## Project Structure
```text
neura-hungarian-lm/
├── train.py
├── config.json
└── README.md
```

## Installation & Setup

### Prerequisites
- Python 3.10+
- GPU with 16GB+ VRAM

### Steps
```bash
git clone https://github.com/zsomborturcsanyi7-lang/neura-hungarian-lm.git
cd neura-hungarian-lm
pip install -r requirements.txt
```

## Usage Examples
```bash
python train.py --config config.json
```

## Status & License
Status: Model Training Code.
License: MIT
