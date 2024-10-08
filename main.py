from fastapi import FastAPI,APIRouter
import uvicorn
app = FastAPI()

v1_router = APIRouter(prefix="/v1")
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)