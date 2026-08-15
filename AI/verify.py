import sys
import os
import json
import time
import argparse

sys.path.append(os.path.dirname(__file__))

from text.starter.text_verify import verify_text
from image.starter.image_verify import verify as verify_image

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_PATH = os.path.join(ROOT_DIR, "dataset", "test")

def print_result(title, result, duration):
    print(f"\n{'-'*60}")
    print(f"{title} (Took {duration:.2f}s)")
    print(f"{'-'*60}")
    print(json.dumps(result, indent=2))
    print(f"{'-'*60}")

text_1 = "OpenAI released GPT-4o in May 2024."
text_2 = "Apple acquired Microsoft in early 2025 to dominate the AI market."
text_3 = "Python was created by Guido van Rossum and first released in 1991."
text_4 = "HTML is a popular programming language used to write backend server logic."
text_5 = "In my opinion, Python is a much more elegant language than JavaScript."
text_6 = "Claude 3.5 Sonnet was released by Anthropic as a major upgrade in AI capabilities."
text_7 = "Devfolio is a popular platform used for hosting and managing hackathons globally."
text_8 = "Elevation Capital is a venture capital firm that focuses on early-stage investments in India."
text_9 = "tech_insider |#| claude 3.5 sonnet released |#| anthropic's claude 3.5 sonnet has been released, showing impressive capabilities in coding, reasoning, and visual tasks compared to previous models."
text_10 = "vedang |#| Saw an UFO |#| Today I saw an UFO in pune hinjewadi |#| 10 aug 2026"

img_1 = os.path.join(TEST_PATH, "real", "2.jpg")
img_2 = os.path.join(TEST_PATH, "ai", "1.jpg")
img_3 = "https://res.cloudinary.com/dfamljkyo/image/upload/v1765866848/v4fh8c9xhegyx2havzar.png"

ACTIVE_TEXT = text_10
ACTIVE_IMAGE = None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SatyaMark Unified Testing Entry Point")
    parser.add_argument("--test", choices=["text", "image", "both"], default="both", help="Which pipeline to test (default: both)")
    args = parser.parse_args()

    if args.test in ["text", "both"]:
        if ACTIVE_TEXT:
            print("\n" + "="*60)
            print("RUNNING SINGLE TEXT VERIFICATION TEST")
            print("="*60)
            print(f"\nTesting Statement: '{ACTIVE_TEXT}'")
            
            start_time = time.time()
            try:
                result = verify_text(ACTIVE_TEXT)
            except Exception as e:
                result = {"error": str(e)}
            duration = time.time() - start_time
            
            print_result("Text Verdict", result, duration)
        else:
            print("\nACTIVE_TEXT is empty or None. Skipping Text Verification.")

    if args.test in ["image", "both"]:
        if ACTIVE_IMAGE:
            print("\n" + "="*60)
            print("RUNNING SINGLE IMAGE VERIFICATION TEST")
            print("="*60)
            print(f"\nTesting Image: '{ACTIVE_IMAGE}'")
            
            start_time = time.time()
            try:
                result = verify_image(ACTIVE_IMAGE)
            except Exception as e:
                result = {"error": str(e)}
            duration = time.time() - start_time
            
            print_result("Image Verdict", result, duration)
        else:
            print("\nACTIVE_IMAGE is empty or None. Skipping Image Verification.")
            
    print("\nTesting Complete!\n")
