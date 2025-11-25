# inference/fatformer.py
"""
FatFormer stub — the original FatFormer HF repo is not available/public,
so we return a neutral probability to keep the pipeline running.

If you later obtain a working model ID or weights, replace this stub with
a proper loader/inference function.
"""
def get_fatformer_prob(image, device=None):
    # Neutral probability (0.5) — acts as 'no signal' so fusion can train.
    return 0.5
