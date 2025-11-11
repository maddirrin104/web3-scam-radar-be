from fastapi import FastAPI
from app.config import settings
from app.routers import score as score_router
from app.routers import rules as rules_router
from app.routers import lookup as lookup_router
from app.routers import logs as logs_router

app = FastAPI(title=settings.api_title, version=settings.api_version, debug=settings.api_debug)

app.include_router(score_router.router)
app.include_router(rules_router.router)
app.include_router(lookup_router.router)
app.include_router(logs_router.router)

@app.get("/")
def root():
    return {"name": settings.api_title, "version": settings.api_version}