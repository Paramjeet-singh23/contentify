from fastapi import FastAPI
from api.endpoints import user

app = FastAPI()

API_PREFIX = "/api"

app.include_router(user.router,tags=["User"], prefix=API_PREFIX)

@app.get("/")
def read_root():
    return {"Hello": "World"}
