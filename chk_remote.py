import torch, glob, os

files = sorted(glob.glob('C:/NeuraNode/bitnet/checkpoints/**/*.pt', recursive=True))
for f in files:
    try:
        c = torch.load(f, map_location='cpu', weights_only=True)
        dirname = os.path.basename(os.path.dirname(f))
        basename = os.path.basename(f)
        loss = c.get('loss', -1)
        if loss != -1:
            loss = round(loss, 4)
        print(f"{dirname}/{basename} | steps={c.get('steps','?')} loss={loss}")
    except Exception as e:
        print(f"{f} error: {e}")
