from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import get_current_user, get_project_service
from app.models.user import User
from app.schemas.project import (
    ProjectCreateRequest,
    ProjectFieldAttachRequest,
    ProjectMemberCreateRequest,
    ProjectResponse,
    ProjectUpdateRequest,
)
from app.services.projects import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    company_id: UUID,
    _: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
) -> list[ProjectResponse]:
    projects = await service.list_by_company(company_id)
    return [ProjectResponse.model_validate(item) for item in projects]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreateRequest,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    project = await service.create(
        company_id=payload.company_id,
        creator_id=current_user.id,
        name=payload.name,
        description=payload.description,
        responsible_by_id=payload.responsible_by_id,
        status_sort=payload.status_sort,
        fields_sort=payload.fields_sort,
    )
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    _: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    project = await service.get(project_id)
    return ProjectResponse.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    payload: ProjectUpdateRequest,
    _: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    project = await service.update(project_id, **payload.model_dump(exclude_none=True))
    return ProjectResponse.model_validate(project)


@router.post("/{project_id}/members", response_model=ProjectResponse)
async def add_project_member(
    project_id: UUID,
    payload: ProjectMemberCreateRequest,
    _: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    project = await service.add_member(project_id, payload.user_id)
    return ProjectResponse.model_validate(project)


@router.post("/{project_id}/fields", response_model=ProjectResponse)
async def attach_company_field(
    project_id: UUID,
    payload: ProjectFieldAttachRequest,
    _: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    project = await service.add_field_link(
        project_id,
        company_field_id=payload.company_field_id,
        required_on_statuses=payload.required_on_statuses,
        style=payload.style,
    )
    return ProjectResponse.model_validate(project)
