# Text Verification Using HuggingFace Models

## Overview
This system performs **end-to-end text verification** using a multi-stage pipeline.  
It analyzes any user-provided statement and determines:
- Whether it is **subjective** or **verifiable**
- Whether the claim is **factually correct**, **incorrect**, or **insufficient**
- Whether to perform web search based on factual confidence
- Whether the claim is supported or contradicted by real-world sources
- A confidence score and a clear explanation

It combines **LLM reasoning**, **web search**, **text extraction**, and **layered verification** to maximize accuracy while avoiding hallucinations.

---

## How It Works

The system processes input in four major phases:

---

## 1. **Summarization**
The user’s statement is cleaned and converted into a short, neutral summary to ensure consistent downstream reasoning.

---

## 2. **Fact Check (LLM-based)**

The summarized statement undergoes structured factual analysis:

### **Fact Check Rules (IMPORTANT)**

1. **If the claim is SUBJECTIVE →**
   - The pipeline **returns immediately**
   - **No web search is performed**
   - Output includes subjective reasoning and accuracy

2. **If the claim is VERIFIABLE but insufficiently supported →**
   - Mark = **INSUFFICIENT**
   - → **Triggers web search verification**

3. **If the claim is Correct/Incorrect but confidence is LOW →**
   - Web search is performed to strengthen or correct the decision

4. **If the claim is Correct/Incorrect with HIGH confidence →**
   - Web search may be **skipped** for efficiency

This ensures:
- Personal opinions are not fact-checked against news sources  
- Weak LLM judgments get strengthened using real evidence  
- Strong LLM judgments avoid unnecessary latency  

---

## 3. **Web Search Verification (When Needed)**

When triggered, the system performs:

### Step-by-step:
1. Converts the claim into a **neutral fact-check query**
2. Fetches URLs using **Google Serper API**
3. Filters irrelevant domains (YouTube, social media, etc.)
4. Downloads article content using **trafilatura**
5. Summarizes extracted text with an LLM
6. Compares summarized web evidence against user summary
7. Produces final verdict and accuracy

---

## 4. **Final Output**
The system returns a structured result containing:
- Final Mark → Correct / Incorrect / Subjective / Insufficient  
- Reason → concise explanation  
- Confidence → 0–100  
- URL → the most relevant article used  
- Fully evidence-backed verification  

---

## Architecture

```
User Input
     |
     v
[ summarize_text.py ]
     |
     v
[ text_fact.py ] ------------------> IF SUBJECTIVE → Final Output
     |
     |-- If INS UFFICIENT or low confidence → continue
     v
[ text_websearch.py ]
     → Rewrite search query
     → Fetch URLs
     → Extract article data
     |
     v
[ text_summarize_web.py ]
     → Summaries of article content
     |
     v
[ text_verify_web.py ]
     → Compare claim vs article evidence
     |
     v
Final Output JSON
```

---

## Role of Each Module

### **1. text_summarize.py**
- Cleans and normalizes user text  
- Generates short, extractive summaries  
- Ensures no hallucination before fact checking  

### **2. text_fact.py**
Runs LLM-based fact evaluation:
- Detects **subjective** content  
- Determines Correct / Incorrect / Insufficient  
- Assigns accuracy  
- Controls web-search trigger logic  

### **3. text_websearch.py**
Handles external search:
- Rewrites claim as powerful fact-check query  
- Fetches URLs via Serper API  
- Extracts clean text articles  

### **4. text_summarize_web.py**
Summarizes long article content:
- Keeps only the information relevant to the claim  

### **5. text_verify_web.py**
Main verification logic:
- Compares claim summary with summarized web info  
- Detects **supporting**, **contradicting**, or **missing** evidence  
- Outputs final verdict and accuracy  

### **6. text_verify.py**
Entry point for backend:
- Summarizes text  
- Fact checks  
- If required → launches web verification  
- Produces **final combined result**  

---

## Final Note

This system is optimized for **factual text verification**, not opinions or predictions.  
By combining:
- Strong LLM reasoning  
- Web-based evidence  
- Multi-layered validation  
- Clear fallback logic  

…it delivers reliable, explainable verification results.

The design is modular — you can swap LLMs, improve search quality, or upgrade summarizers without breaking the pipeline.

---

