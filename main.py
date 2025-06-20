from fastapi import FastAPI, Body
from langdetect import detect
from spellchecker import SpellChecker
# import language_tool_python

app = FastAPI()
# tool = language_tool_python.LanguageTool('en-US')
spell = SpellChecker()

@app.get("/")
def root():
    return {"message": "Server is up"}

@app.post("/preprocess")
def preprocess(input_text: str = Body(...)):
    # Deteksi bahasa
    lang = detect(input_text)

    # Spell check (hanya kalau Inggris)
    if lang == 'en':
        words = input_text.split()
        corrected_words = [spell.correction(w) or w for w in words]
        typo_corrected = ' '.join(corrected_words)

        # Grammar check
        # matches = tool.check(typo_corrected)
        # grammar_issues = [m.message for m in matches]
    else:
        typo_corrected = input_text
        # grammar_issues = []

    # Dummy loanword correction (nanti lo tambahin logic beneran)
    loanword_corrected = typo_corrected  # sementara

    return {
        "original": input_text,
        "detected_lang": lang,
        "typo_corrected": typo_corrected,
        "loanword_corrected": loanword_corrected,
        # "grammar_issues": grammar_issues
    }
