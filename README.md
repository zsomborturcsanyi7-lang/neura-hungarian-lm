# NEURA — Magyar AI Nyelvi Modell

**355M paraméteres magyar nyelvi modell**, saját architektúrával (GQA + SwiGLU + RMSNorm), RTX 3070 8GB GPU-n trenírozva.

## Modell architektúra
- 24 réteg, 1024 dimenzió, 16 attention fej, 4 KV fej
- SentencePiece 32K tokenizer
- Training adat: 2.53B token (OpenSubtitles + HunSum-2)
- Legjobb PPL: 48.3 (390K lépés)

## Fájlok
| Fájl | Leírás |
|------|--------|
| `neura_explorer.py` | Modell vizsgáló — forward-pass hook-ok, neuron aktiváció |
| `neura_forge_v1.pt` | NEURA Forge modell (1078 neuron törölve/cserélve) |
| `neura_monitor.py` | Training automatikus monitor + újraindítás |
| `continue_300m.py` | Training folytató script |
| `train_v2.py` | Új training script |

## Kutatási Paper-ek
A Desktop-on: `neura_research_paper_01-05_*.md`
1. Training Dynamics & Loss Landscape
2. Neuron Specialization & Sparsity
3. Attention Mechanism & Layer Hierarchy
4. Why 355M Can't Reason (& How To Fix It)
5. Practical Guide to Model Editing

## Használat
```bash
# Modell betöltése
python neura_explorer.py

# Training folytatása (RTX 3070)
python continue_300m.py
```

## Függőségek
- PyTorch 2.x + CUDA
- SentencePiece
- NumPy
