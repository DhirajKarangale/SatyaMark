from AI.img_ml.models.model_wrappers import get_mantranet_model
from AI.img_ml.models.model_wrappers import get_ghostnet_model
from AI.img_ml.models.model_wrappers import get_dino_model
from AI.img_ml.models.model_wrappers import get_clip_model_h14
from AI.img_ml.models.model_wrappers import get_clip_model_bigg

print("\nLoading CLIP ViT-B/32...")
try:
    proc, model, device = get_clip_model_bigg()
    print("CLIP B/32 loaded successfully on:", device)
except Exception as e:
    print("ERROR loading CLIP B/32:", e)


print("\nLoading CLIP H14...")
try:
    proc, model, device = get_clip_model_h14()
    print("CLIP H14 loaded successfully on:", device)
except Exception as e:
    print("ERROR loading CLIP H14:", e)


print("\nLoading DINOv2...")
try:
    proc, model, device = get_dino_model()
    print("DINO loaded successfully on:", device)
except Exception as e:
    print("ERROR loading DINO:", e)



print("\nLoading GhostNet...")
try:
    proc, model, device = get_ghostnet_model()
    print("GhostNet loaded successfully on:", device)
except Exception as e:
    print("ERROR loading GhostNet:", e)


print("\nLoading MantraNet...")
try:
    proc, model, device = get_mantranet_model()
    print("MantraNet loaded successfully on:", device)
except Exception as e:
    print("ERROR loading MantraNet:", e)
