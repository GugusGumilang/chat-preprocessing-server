from fastapi import FastAPI, Body, Request
import spacy
import errant
from transformers import pipeline
import subprocess
import traceback
import logging
import time
import re

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# ⚡️ INIT spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logging.warning("Model spaCy tidak ditemukan. Mendownload...")
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

# ⚡️ INIT ERRANT & grammar corrector
annotator = errant.load("en")
corrector = pipeline("text2text-generation", model="prithivida/grammar_error_correcter_v1", device=-1)

# ⚡️ Map ERRANT tag to readable label
error_mapping = {
    "R:VERB:TENSE": "Tenses",
    "R:VERB:FORM": "Verb Form",
    "R:VERB:SVA": "Subject-Verb Agreement",
    "R:VERB:INFL": "Verb Inflection",
    "R:VERB:AGR": "Verb Agreement",
    "R:NOUN:NUM": "Singular/Plural Forms",
    "R:NOUN:INFL": "Noun Inflection",
    "R:PRON": "Pronouns",
    "M:DET": "Articles",
    "R:DET": "Articles",
    "U:DET": "Articles",
    "M:PREP": "Prepositions",
    "R:PREP": "Prepositions",
    "U:PREP": "Prepositions",
    "R:ORTH": "Capitalization",
    "R:PUNCT": "Punctuation",
    "M:PUNCT": "Punctuation",
    "U:PUNCT": "Punctuation",
    "R:SPELL": "Spelling Errors",
    "R:ADV": "Adverb Errors",
    "M:ADV": "Adverb Errors",
    "U:ADV": "Adverb Errors",
    "R:ADJ": "Adjective Errors",
    "M:ADJ": "Adjective Errors",
    "U:ADJ": "Adjective Errors",
    "R:CONJ": "Conjunction Errors",
    "M:CONJ": "Conjunction Errors",
    "U:CONJ": "Conjunction Errors",
    "R:PART": "Particle Errors",
    "R:WO": "Word Order Errors",
    "R:OTHER": "Other Errors",
    "M:OTHER": "Other Errors",
    "U:OTHER": "Other Errors",
    "R:RED": "Redundancy",
}

def map_error(tag: str) -> str:
    return error_mapping.get(tag, tag)

@app.get("/")
def root():
    return {"message": "Server is running."}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/process_minimal")
def process_minimal(input_text: str = Body(...)):
    start_time = time.time()

    lang = detect_language(input_text)
    if lang != "en":
        return {"detected_lang": lang, "results": []}

    results = []

    sentences = list(nlp(input_text).sents)
    corrected_pairs = []

    for sent in sentences:
        corrected_text = corrector(sent.text, num_return_sequences=1)[0]["generated_text"]
        corrected_pairs.append((sent.text, corrected_text))

    for original, corrected in corrected_pairs:
        edits = annotator.annotate(nlp(original), nlp(corrected))
        errors = [
            {
                "original_error": e.o_str,
                "category": map_error(e.type)
            }
            for e in edits
        ]
        results.append({
            "original": original,
            "corrected": corrected,
            "errors": errors
        })

    duration = round(time.time() - start_time, 2)
    logging.info(f"✅ Processing time: {duration}s")

    return {
        "detected_lang": lang,
        "results": results
    }

@app.middleware("http")
async def error_handling(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}

def detect_language(text: str) -> str:
    pattern = r"\b(the|we|they|he|she|may|who|whom|her|his|have|had|is|am|you|and|are|hello|good|thanks|how|what|where|why|when|i|me|your|from|to|at|on|in|it|for|of|a|an|do|does|did|can|should|would|will|won't|don't|can't|shouldn't|wouldn't|isn't|isnt|was|were|be|being|been)\b"
    return "en" if re.search(pattern, text, re.IGNORECASE) else "id"
