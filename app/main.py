from fastapi import FastAPI

app = FastAPI()

BASE_PATH = "/api/v1"

@app.get("/")
def root():
    return {
        "service": "ReSynth - A Grounded Research Engine",
        "status": "running"
    }


@app.get(f"{BASE_PATH}/health")
def health():
    return {
        "status": "ok"
    }
