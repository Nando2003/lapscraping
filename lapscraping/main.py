from fastapi import FastAPI
from routes import load_routes

app = FastAPI()
load_routes(app)
