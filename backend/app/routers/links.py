from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    BulkCreateLinkRequest,
    CreateLinkRequest,
    LinkListResponse,
    LinkResponse,
)
from app.services import link_service

router = APIRouter()


@router.post("", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
async def create_link(
    payload: CreateLinkRequest,
    db: AsyncSession = Depends(get_db),
) -> LinkResponse:
    return await link_service.create_link(db, payload)


@router.post("/bulk", response_model=LinkListResponse, status_code=status.HTTP_201_CREATED)
async def create_links_bulk(
    payload: BulkCreateLinkRequest,
    db: AsyncSession = Depends(get_db),
) -> LinkListResponse:
    items = await link_service.create_links_bulk(db, payload)
    return LinkListResponse(items=items, total=len(items))


@router.get("", response_model=LinkListResponse)
async def list_links(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> LinkListResponse:
    items, total = await link_service.list_links(db, limit=limit, offset=offset)
    return LinkListResponse(items=items, total=total)


@router.get("/{code}", response_model=LinkResponse)
async def get_link(
    code: str,
    db: AsyncSession = Depends(get_db),
) -> LinkResponse:
    link = await link_service.get_link_by_code(db, code)
    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")
    return link_service.to_link_response(link)


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    code: str,
    db: AsyncSession = Depends(get_db),
) -> Response:
    await link_service.delete_link(db, code)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
