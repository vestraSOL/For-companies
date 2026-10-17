from fastapi import APIRouter

from app.api.routes import (
    auth,
    catalogs,
    comments,
    companies,
    federations,
    profile,
    projects,
    reminders,
    tasks,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(profile.router)
api_router.include_router(users.router)
api_router.include_router(federations.router)
api_router.include_router(companies.router)
api_router.include_router(projects.router)
api_router.include_router(tasks.router)
api_router.include_router(comments.router)
api_router.include_router(reminders.router)
api_router.include_router(catalogs.router)
