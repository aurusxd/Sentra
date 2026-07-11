from fastapi import APIRouter, Depends, File, UploadFile, status

from backend.core.security import get_current_user
from backend.database.models.user import User
from backend.schemas.knowledge_schema import KnowledgeFileRead
from backend.services.employee_service import EmployeeService
from backend.services.knowledge_file_service import KnowledgeFileService
from backend.utils.rate_limit import rate_limit


router = APIRouter(
    prefix="/employees/{employee_id}/knowledge",
    tags=["Knowledge"],
)

knowledge_file_service = KnowledgeFileService()
employee_service = EmployeeService()


@router.get(
    "/",
    response_model=list[KnowledgeFileRead],
)
async def get_knowledge_files(
    employee_id: int,
    current_user: User = Depends(get_current_user),
):
    await employee_service.get_by_id(
        employee_id=employee_id,
        owner_id=current_user.id,
    )

    return await knowledge_file_service.get_all_by_employee(
        employee_id=employee_id,
    )


@router.post(
    "/upload",
    response_model=KnowledgeFileRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit("knowledge-upload", 20, 3600))],
)
async def upload_knowledge_file(
    employee_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    await employee_service.get_by_id(
        employee_id=employee_id,
        owner_id=current_user.id,
    )

    return await knowledge_file_service.upload(
        employee_id=employee_id,
        upload_file=file,
    )


@router.delete(
    "/{file_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_knowledge_file(
    employee_id: int,
    file_id: int,
    current_user: User = Depends(get_current_user),
):
    await employee_service.get_by_id(
        employee_id=employee_id,
        owner_id=current_user.id,
    )

    return await knowledge_file_service.delete(
        file_id=file_id,
        employee_id=employee_id,
    )


@router.post(
    "/{file_id}/reindex",
    response_model=KnowledgeFileRead,
)
async def reindex_knowledge_file(
    employee_id: int,
    file_id: int,
    current_user: User = Depends(get_current_user),
):
    await employee_service.get_by_id(
        employee_id=employee_id,
        owner_id=current_user.id,
    )

    file = await knowledge_file_service.mark_processing(
        file_id=file_id,
        employee_id=employee_id,
    )

    return file
