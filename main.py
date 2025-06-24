from fastapi import FastAPI, Body
from langdetect import detect
from spellchecker import SpellChecker
import spacy
import errant
from transformers import pipeline

app = FastAPI()

# ⚡️ Init Model
nlp = spacy.load("en_core_web_sm")          
annotator = errant.load("en")
corrector = pipeline("text2text-generation", model="prithivida/grammar_error_correcter_v1")
spell = SpellChecker()

# ⚡️ 2️⃣ Map Error ERRANT
error_mapping = {
    # Verb-related
    "R:VERB:TENSE": "Tenses",
    "R:VERB:FORM": "Verb Form",
    "R:VERB:SVA": "Subject-Verb Agreement",
    "R:VERB:INFL": "Verb Inflection",
    "R:VERB:AGR": "Verb Agreement",

    # Noun-related
    "R:NOUN:NUM": "Singular/Plural Forms",
    "R:NOUN:INFL": "Noun Inflection",

    # Pronouns
    "R:PRON": "Pronouns",

    # Articles/Determiners
    "M:DET": "Articles",
    "R:DET": "Articles",
    "U:DET": "Articles",

    # Prepositions
    "M:PREP": "Prepositions",
    "R:PREP": "Prepositions",
    "U:PREP": "Prepositions",

    # Capitalization
    "R:ORTH": "Capitalization",

    # Punctuation
    "R:PUNCT": "Punctuation",
    "M:PUNCT": "Punctuation",
    "U:PUNCT": "Punctuation",

    # Spelling
    "R:SPELL": "Spelling Errors",

    # Adverbs
    "R:ADV": "Adverb Errors",
    "M:ADV": "Adverb Errors",
    "U:ADV": "Adverb Errors",

    # Adjectives
    "R:ADJ": "Adjective Errors",
    "M:ADJ": "Adjective Errors",
    "U:ADJ": "Adjective Errors",

    # Conjunctions
    "R:CONJ": "Conjunction Errors",
    "M:CONJ": "Conjunction Errors",
    "U:CONJ": "Conjunction Errors",

    # Particles
    "R:PART": "Particle Errors",

    # Word Order
    "R:WO": "Word Order Errors",

    # Others
    "R:OTHER": "Other Errors",
    "M:OTHER": "Other Errors",
    "U:OTHER": "Other Errors",
}

def map_error(tag):
    """Map ERRANT tag to human-readable category."""
    return error_mapping.get(tag, tag)

@app.get("/")
def root():
    return {"message": "Server is up"}

@app.post("/process_minimal")
def process_minimal(input_text: str = Body(...)):
    """Return minimal output for GPT."""
    lang = detect(input_text)

    if lang != "en":
        return {
            "detected_lang": lang,
            "results": []
        }

    results = []
    for sent in list(nlp(input_text).sents):
        # Typo Correction
        words = sent.text.split()
        corrected_words = [spell.correction(w) or w for w in words]
        typo_corrected = " ".join(corrected_words)

        # Grammar Correction
        corrected = corrector(typo_corrected, num_return_sequences=1)[0]["generated_text"]

        # ERRANT Annotations
        edits = annotator.annotate(nlp(sent.text), nlp(corrected))
        results.append({
            "corrected": corrected,
            "errors": [
                {
                    "original_error": e.o_str,
                    "category": map_error(e.type)
                } for e in edits
            ]
        })

    return {
        "detected_lang": lang,
        "results": results
    }
