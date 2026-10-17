from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_db_session
from app.models.user import User
from app.repositories.users import UserRepository
from app.schemas.common import UserSummary

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/search", response_model=list[UserSummary])
async def search_users(
    q: str = Query(min_length=1),
    _: User = Depends(get_current_user),
    session=Depends(get_db_session),
) -> list[UserSummary]:
    users = await UserRepository(session).search(search=q)
    return [UserSummary.model_validate(user) for user in users]
