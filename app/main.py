# AutomateOS main application file
from fastapi import FastAPI

app = FastAPI(
    title="AutomateOS",
    description="API for automating operating system tasks",
    version="0.1.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to AutomateOS API"}