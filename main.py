from fastapi import FastAPI, Body

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Server is up"}

@app.post("/preprocess")
def preprocess(input_text: str = Body(...)):
    return {
        "original": input_text,
        "typo_corrected": input_text,
        "loanword_corrected": input_text,
        "grammar_issues": []
    }
