from __future__ import annotations

from uuid import UUID

from sqladmin import ModelView
from sqladmin.filters import BooleanFilter, OperationColumnFilter
from starlette.requests import Request

from app.models.catalog import Catalog, CatalogField, CatalogRecord
from app.models.comment import Comment
from app.models.company import Company, CompanyField, CompanyMember, Tag
from app.models.federation import Federation, FederationMember
from app.models.project import Project, ProjectField, ProjectMember, ProjectStatus
from app.models.reminder import Reminder
from app.models.task import Task
from app.models.user import User

AUDIT_COLUMNS = ["created_at", "updated_at", "deleted_at"]


class BaseAdminView(ModelView):
    page_size = 25
    can_export = False
    form_include_pk = True
    form_excluded_columns = AUDIT_COLUMNS
    column_default_sort = ("created_at", True)

    async def on_model_change(
        self,
        data: dict,
        model,
        is_created: bool,
        request: Request,
    ) -> None:
        if (
            is_created
            and hasattr(model, "created_by_id")
            and "created_by_id" not in data
        ):
            admin_user = getattr(request.state, "admin_user", None)
            if admin_user is not None:
                data["created_by_id"] = admin_user.id

    async def _resolve_related(self, value, model_class):
        if value is None or isinstance(value, model_class):
            return value

        try:
            pk = UUID(str(value))
        except ValueError:
            pk = value

        async with self.session_maker(expire_on_commit=False) as session:
            return await session.get(model_class, pk)


class FederationScopedAdminView(BaseAdminView):
    async def on_model_change(
        self,
        data: dict,
        model,
        is_created: bool,
        request: Request,
    ) -> None:
        await super().on_model_change(data, model, is_created, request)
        if "federation_id" not in data:
            federation = data.get("federation")
            company = data.get("company")
            catalog = data.get("catalog")
            task = data.get("task")
            if federation is not None:
                federation_obj = await self._resolve_related(federation, Federation)
                data["federation_id"] = (
                    federation_obj.id if federation_obj else federation
                )
            elif company is not None:
                company_obj = await self._resolve_related(company, Company)
                if company_obj is not None:
                    data["federation_id"] = company_obj.federation_id
            elif catalog is not None:
                catalog_obj = await self._resolve_related(catalog, Catalog)
                if catalog_obj is not None:
                    data["federation_id"] = catalog_obj.federation_id
            elif task is not None:
                task_obj = await self._resolve_related(task, Task)
                if task_obj is not None:
                    data["federation_id"] = task_obj.federation_id


class CompanyScopedAdminView(FederationScopedAdminView):
    async def on_model_change(
        self,
        data: dict,
        model,
        is_created: bool,
        request: Request,
    ) -> None:
        await super().on_model_change(data, model, is_created, request)
        if "company_id" not in data:
            company = data.get("company")
            project = data.get("project")
            catalog = data.get("catalog")
            task = data.get("task")
            if company is not None:
                company_obj = await self._resolve_related(company, Company)
                data["company_id"] = company_obj.id if company_obj else company
            elif project is not None:
                project_obj = await self._resolve_related(project, Project)
                if project_obj is not None:
                    data["company_id"] = project_obj.company_id
            elif catalog is not None:
                catalog_obj = await self._resolve_related(catalog, Catalog)
                if catalog_obj is not None:
                    data["company_id"] = catalog_obj.company_id
            elif task is not None:
                task_obj = await self._resolve_related(task, Task)
                if task_obj is not None:
                    data["company_id"] = task_obj.company_id


class UserAdmin(BaseAdminView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-users"
    category = "Accounts"
    can_create = False
    can_delete = False
    column_list = [
        User.id,
        User.email,
        User.first_name,
        User.last_name,
        User.phone,
        User.is_active,
        User.is_valid,
        User.created_at,
    ]
    column_details_list = [
        User.id,
        User.email,
        User.first_name,
        User.last_name,
        User.middle_name,
        User.phone,
        User.is_active,
        User.is_valid,
        User.color,
        User.has_photo,
        User.preferences,
        User.meta,
        User.valid_at,
        User.validation_sent_at,
        User.created_at,
        User.updated_at,
        User.deleted_at,
    ]
    column_searchable_list = [
        User.email,
        User.first_name,
        User.last_name,
        User.middle_name,
        User.phone,
    ]
    column_sortable_list = [User.email, User.created_at, User.valid_at]
    column_filters = [
        BooleanFilter(User.is_active),
        BooleanFilter(User.is_valid),
    ]
    form_columns = [
        User.email,
        User.first_name,
        User.last_name,
        User.middle_name,
        User.phone,
        User.is_active,
        User.is_valid,
        User.color,
        User.has_photo,
        User.preferences,
        User.valid_at,
        User.validation_sent_at,
    ]


class FederationAdmin(BaseAdminView, model=Federation):
    name = "Federation"
    name_plural = "Federations"
    icon = "fa-solid fa-building-columns"
    category = "Structure"
    column_list = [
        Federation.id,
        Federation.name,
        Federation.created_by,
        Federation.created_at,
    ]
    column_details_list = [
        Federation.id,
        Federation.name,
        Federation.created_by,
        Federation.meta,
        Federation.created_at,
        Federation.updated_at,
        Federation.deleted_at,
    ]
    column_searchable_list = [Federation.name]
    column_sortable_list = [Federation.name, Federation.created_at]
    form_columns = [Federation.name]


class FederationMemberAdmin(BaseAdminView, model=FederationMember):
    name = "Federation Member"
    name_plural = "Federation Members"
    icon = "fa-solid fa-user-group"
    category = "Structure"
    column_list = [
        FederationMember.federation,
        FederationMember.user,
        FederationMember.created_at,
    ]
    column_sortable_list = [FederationMember.created_at]
    form_columns = [
        FederationMember.federation,
        FederationMember.user,
    ]


class CompanyAdmin(FederationScopedAdminView, model=Company):
    name = "Company"
    name_plural = "Companies"
    icon = "fa-solid fa-building"
    category = "Structure"
    column_list = [
        Company.id,
        Company.name,
        Company.federation,
        Company.created_by,
        Company.created_at,
    ]
    column_details_list = [
        Company.id,
        Company.name,
        Company.federation,
        Company.created_by,
        Company.meta,
        Company.sms_options,
        Company.created_at,
        Company.updated_at,
        Company.deleted_at,
    ]
    column_searchable_list = [Company.name]
    column_sortable_list = [Company.name, Company.created_at]
    form_columns = [
        Company.federation,
        Company.name,
        Company.sms_options,
    ]


class CompanyMemberAdmin(FederationScopedAdminView, model=CompanyMember):
    name = "Company Member"
    name_plural = "Company Members"
    icon = "fa-solid fa-users-gear"
    category = "Structure"
    column_list = [
        CompanyMember.company,
        CompanyMember.user,
        CompanyMember.created_at,
    ]
    column_sortable_list = [CompanyMember.created_at]
    form_columns = [
        CompanyMember.company,
        CompanyMember.user,
    ]


class CompanyFieldAdmin(BaseAdminView, model=CompanyField):
    name = "Company Field"
    name_plural = "Company Fields"
    icon = "fa-solid fa-table-columns"
    category = "Metadata"
    column_list = [
        CompanyField.company_id,
        CompanyField.name,
        CompanyField.hash,
        CompanyField.data_type,
        CompanyField.created_at,
    ]
    column_searchable_list = [CompanyField.name, CompanyField.hash]
    column_sortable_list = [CompanyField.name, CompanyField.created_at]
    form_columns = [
        CompanyField.company_id,
        CompanyField.name,
        CompanyField.hash,
        CompanyField.description,
        CompanyField.icon,
        CompanyField.data_type,
        CompanyField.required_on_statuses,
        CompanyField.style,
    ]


class TagAdmin(FederationScopedAdminView, model=Tag):
    name = "Tag"
    name_plural = "Tags"
    icon = "fa-solid fa-tags"
    category = "Metadata"
    column_list = [Tag.name, Tag.company, Tag.created_by, Tag.color, Tag.created_at]
    column_searchable_list = [Tag.name]
    column_sortable_list = [Tag.name, Tag.created_at]
    form_columns = [
        Tag.company,
        Tag.name,
        Tag.color,
    ]


class CatalogAdmin(CompanyScopedAdminView, model=Catalog):
    name = "Catalog"
    name_plural = "Catalogs"
    icon = "fa-solid fa-book"
    category = "Structure"
    column_list = [
        Catalog.id,
        Catalog.name,
        Catalog.company,
        Catalog.created_by,
        Catalog.created_at,
    ]
    column_searchable_list = [Catalog.name, Catalog.description]
    column_sortable_list = [Catalog.name, Catalog.created_at]
    form_columns = [
        Catalog.company,
        Catalog.name,
        Catalog.description,
    ]


class CatalogFieldAdmin(BaseAdminView, model=CatalogField):
    name = "Catalog Field"
    name_plural = "Catalog Fields"
    icon = "fa-solid fa-list-check"
    category = "Metadata"
    column_list = [
        CatalogField.catalog,
        CatalogField.data_catalog,
        CatalogField.name,
        CatalogField.hash,
        CatalogField.data_type,
        CatalogField.created_at,
    ]
    column_searchable_list = [CatalogField.name, CatalogField.hash]
    column_sortable_list = [CatalogField.name, CatalogField.created_at]
    form_columns = [
        CatalogField.catalog,
        CatalogField.data_catalog,
        CatalogField.name,
        CatalogField.hash,
        CatalogField.data_type,
    ]


class CatalogRecordAdmin(CompanyScopedAdminView, model=CatalogRecord):
    name = "Catalog Record"
    name_plural = "Catalog Records"
    icon = "fa-solid fa-rectangle-list"
    category = "Metadata"
    column_list = [
        CatalogRecord.catalog,
        CatalogRecord.created_by,
        CatalogRecord.created_at,
    ]
    column_sortable_list = [CatalogRecord.created_at]
    form_columns = [
        CatalogRecord.catalog,
        CatalogRecord.field_values,
        CatalogRecord.entities,
    ]


class ProjectAdmin(CompanyScopedAdminView, model=Project):
    name = "Project"
    name_plural = "Projects"
    icon = "fa-solid fa-diagram-project"
    category = "Work"
    column_list = [
        Project.id,
        Project.name,
        Project.company,
        Project.created_by,
        Project.responsible_by,
        Project.status_code,
        Project.created_at,
    ]
    column_details_list = [
        Project.id,
        Project.company,
        Project.created_by,
        Project.responsible_by,
        Project.name,
        Project.description,
        Project.options,
        Project.status_flow,
        Project.status_sort,
        Project.fields_sort,
        Project.status_code,
        Project.meta,
        Project.created_at,
        Project.updated_at,
        Project.deleted_at,
    ]
    column_searchable_list = [Project.name, Project.description]
    column_sortable_list = [Project.name, Project.status_code, Project.created_at]
    form_columns = [
        Project.company,
        Project.responsible_by,
        Project.name,
        Project.description,
        Project.options,
        Project.status_flow,
        Project.status_sort,
        Project.fields_sort,
        Project.status_code,
    ]


class ProjectMemberAdmin(BaseAdminView, model=ProjectMember):
    name = "Project Member"
    name_plural = "Project Members"
    icon = "fa-solid fa-people-group"
    category = "Work"
    column_list = [
        ProjectMember.project,
        ProjectMember.user,
        ProjectMember.created_at,
    ]
    column_sortable_list = [ProjectMember.created_at]
    form_columns = [
        ProjectMember.project,
        ProjectMember.user,
    ]


class ProjectFieldAdmin(BaseAdminView, model=ProjectField):
    name = "Project Field"
    name_plural = "Project Fields"
    icon = "fa-solid fa-sliders"
    category = "Metadata"
    column_list = [
        ProjectField.project,
        ProjectField.company_field,
        ProjectField.created_at,
    ]
    column_sortable_list = [ProjectField.created_at]
    form_columns = [
        ProjectField.project,
        ProjectField.company_field,
        ProjectField.required_on_statuses,
        ProjectField.style,
    ]


class ProjectStatusAdmin(CompanyScopedAdminView, model=ProjectStatus):
    name = "Project Status"
    name_plural = "Project Statuses"
    icon = "fa-solid fa-list-ol"
    category = "Metadata"
    column_list = [
        ProjectStatus.project,
        ProjectStatus.number,
        ProjectStatus.name,
        ProjectStatus.color,
        ProjectStatus.created_at,
    ]
    column_searchable_list = [ProjectStatus.name]
    column_sortable_list = [
        ProjectStatus.number,
        ProjectStatus.name,
        ProjectStatus.created_at,
    ]
    form_columns = [
        ProjectStatus.project,
        ProjectStatus.number,
        ProjectStatus.name,
        ProjectStatus.color,
        ProjectStatus.description,
    ]


class TaskAdmin(BaseAdminView, model=Task):
    name = "Task"
    name_plural = "Tasks"
    icon = "fa-solid fa-list-check"
    category = "Work"
    can_create = False
    can_edit = False
    can_delete = False
    column_list = [
        Task.sequential_id,
        Task.name,
        Task.project_id,
        Task.status,
        Task.priority,
        Task.responsible_by_id,
        Task.finish_to,
        Task.created_at,
    ]
    column_details_list = [
        Task.id,
        Task.sequential_id,
        Task.federation_id,
        Task.company_id,
        Task.project_id,
        Task.parent_task_id,
        Task.name,
        Task.description,
        Task.icon,
        Task.created_by_id,
        Task.responsible_by_id,
        Task.implement_by_id,
        Task.managed_by_id,
        Task.finished_by_id,
        Task.coworker_ids,
        Task.watcher_ids,
        Task.people_ids,
        Task.path,
        Task.is_epic,
        Task.status,
        Task.priority,
        Task.field_values,
        Task.meta,
        Task.task_entities,
        Task.stops,
        Task.activity_at,
        Task.finish_to,
        Task.finished_at,
        Task.created_at,
        Task.updated_at,
        Task.deleted_at,
    ]
    column_searchable_list = [Task.name, Task.description]
    column_sortable_list = [
        Task.sequential_id,
        Task.status,
        Task.priority,
        Task.finish_to,
        Task.created_at,
    ]
    column_filters = [
        BooleanFilter(Task.is_epic),
        OperationColumnFilter(Task.status),
        OperationColumnFilter(Task.priority),
    ]


class CommentAdmin(BaseAdminView, model=Comment):
    name = "Comment"
    name_plural = "Comments"
    icon = "fa-solid fa-comments"
    category = "Work"
    column_list = [
        Comment.task,
        Comment.created_by,
        Comment.pin,
        Comment.created_at,
    ]
    column_searchable_list = [Comment.body]
    column_sortable_list = [Comment.pin, Comment.created_at]
    column_filters = [BooleanFilter(Comment.pin)]
    form_columns = [
        Comment.task,
        Comment.reply_to,
        Comment.body,
        Comment.mentioned_user_ids,
        Comment.likes,
        Comment.pin,
    ]


class ReminderAdmin(BaseAdminView, model=Reminder):
    name = "Reminder"
    name_plural = "Reminders"
    icon = "fa-solid fa-bell"
    category = "Work"
    column_list = [
        Reminder.task,
        Reminder.created_by,
        Reminder.assignee,
        Reminder.type,
        Reminder.status,
        Reminder.date_from,
        Reminder.created_at,
    ]
    column_searchable_list = [Reminder.description, Reminder.comment, Reminder.type]
    column_sortable_list = [
        Reminder.status,
        Reminder.date_from,
        Reminder.date_to,
        Reminder.created_at,
    ]
    column_filters = [
        OperationColumnFilter(Reminder.type),
        OperationColumnFilter(Reminder.status),
    ]
    form_columns = [
        Reminder.task,
        Reminder.assignee,
        Reminder.description,
        Reminder.comment,
        Reminder.type,
        Reminder.status,
        Reminder.date_from,
        Reminder.date_to,
    ]


ADMIN_VIEWS = (
    UserAdmin,
    FederationAdmin,
    FederationMemberAdmin,
    CompanyAdmin,
    CompanyMemberAdmin,
    CompanyFieldAdmin,
    TagAdmin,
    CatalogAdmin,
    CatalogFieldAdmin,
    CatalogRecordAdmin,
    ProjectAdmin,
    ProjectMemberAdmin,
    ProjectFieldAdmin,
    ProjectStatusAdmin,
    TaskAdmin,
    CommentAdmin,
    ReminderAdmin,
)
