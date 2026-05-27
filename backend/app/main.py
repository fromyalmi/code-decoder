from fastapi import FastAPI

app = FastAPI(title="Code Decoder API")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
