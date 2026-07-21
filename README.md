# NEURA 300M — 355M paraméteres magyar nyelvi modell

**Status:** ✅ Working — modell betanítva, szöveggenerálás tesztelve 390K step-nél (PPL=48.3)

355M paraméteres magyar nyelvi modell egyedi architektúrával (GQA + SwiGLU + RMSNorm), RTX 3070 8GB GPU-n tanítva.

## ⚠️ THIS PROJECT IS UNFINISHED — FEEL FREE TO CONTINUE IT ⚠️

**Ez a projekt NINCS KÉSZEN. Bárki folytathatja, aki akarja!**
Ezt a projektet Zsombi & Hermes Agent (Nous Research) közösen fejlesztette, de egyik projekt sincs 100%-osan befejezve. Ha tetszik az ötlet és tovább fejlesztenéd, nyugodtan fork-old, folytasd, és csinálj belőle valami nagyszerűt!

---

## Architektúra
- 24 réteg, 1024 dimenzió, 16 attention head, 4 KV head
- SentencePiece 32K tokenizer
- Training data: 2.53B token (OpenSubtitles + HunSum-2)
- Best PPL: 48.3 (390K steps)

## Fájlok
| Fájl | Leírás |
|------|--------|
| `neura.py` | Modell architektúra |
| `sft_train.py` | SFT training |
| `test_neura.py` | Teszt |
| `neura_test.py` | Modell teszt |
| `deploy_sft.py` | Deployment |

## Fejlesztő
Zsombi & Hermes Agent (Nous Research)
