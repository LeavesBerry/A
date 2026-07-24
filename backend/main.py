import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import PUBLIC_DIR
from database import Base, engine
from exceptions import register_exception_handlers
from routers import anno_routes, auth_routes, coll_routes, feedback_routes, system, user_routes, text_routes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(PUBLIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=PUBLIC_DIR), name="static")

register_exception_handlers(app)

app.include_router(system.router)
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(coll_routes.router)
app.include_router(anno_routes.router)
app.include_router(feedback_routes.router)
app.include_router(text_routes.router)

Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
