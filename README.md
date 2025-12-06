# SatyaMark AI

SatyaMark is an AI-powered, centralized verification service designed to provide a universal “mark of truth” for digital content. It helps detect misinformation and AI-generated content, providing transparent, evidence-backed verdicts across platforms.

## Setup

- Create a `.env` file in the root folder.

1. **AI:** Contains AI modules and data

   - Add your Hugging Face token in `.env`:
   ```env
   HF_TOKEN=your_hugging_face_token
   ```

   - Navigate to the AI folder:
   ```bash
   cd "E:\Full Stack\SatyaMark\AI"
   ```

   - Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\AI\venv\Scripts\activate  # Windows
   source venv/bin/activate   # Linux/macOS
   ```

   - Install dependencies:
   ```bash
   ca AI
   pip install -r requirements.txt
   ```

   ### Usage

   - Add new LLMs in `LLMs.json` (basic structure shown below):
   ```json
   [
     {
       "name": "model_name",
       "model_id": "huggingface_model_id",
       "task": "conversational or text-generation",
       "max_new_tokens": 256,
       "temperature": 0.2
     }
   ]
   ```

   - Access LLMs using the `get_llm` function from `connect.py`:
   ```python
   from connect import get_llm

   # Get any LLM from LLMs.json
   llm = get_llm("model_name")
   response = llm("Your input text here")
   print(response)
   ```

   - `main.py` is the main file to run for testing AI modules.

   - Notes:
     - Only include essential dependencies in `requirements.txt`.
     - Activate the virtual environment before running scripts.
     - LLMs in `LLMs.json` can be freely added or modified.

     run
     python -m AI.text.text_verify
     python -m AI.img_forensic.img_forensic_evaluate

     python -m AI.img_ml.fusion.train_fusion
     python -m AI.img_ml.scripts.make_dataset_csv

     pip install --index-url https://download.pytorch.org/whl/cu121 -- install to this to check GPU
     python -c "import torch;print(torch.cuda.is_available(), torch.cuda.get_device_name(0))" -- check GPU

2. **Frontend:** Currently empty
3. **Backend:** Currently empty
































Add Submodule 
git submodule add https://github.com/DhirajKarangale/ai-text-verify-worker AI/ai-text-verify-worker

git submodule add https://github.com/DhirajKarangale/ai-image-forensic-verify-worker AI/ai-image-forensic-verify-worker