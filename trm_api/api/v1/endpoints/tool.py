from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from trm_api.models.tool import Tool, ToolCreate, ToolUpdate
from trm_api.services.tool_service import tool_service, ToolService

router = APIRouter()

@router.post("/", response_model=Tool, status_code=status.HTTP_201_CREATED)
def create_tool(
    tool_in: ToolCreate,
    service: ToolService = Depends(lambda: tool_service)
):
    """
    Create a new Tool.
    """
    return service.create_tool(tool_create=tool_in)

@router.get("/{tool_id}", response_model=Tool)
def get_tool(
    tool_id: str,
    service: ToolService = Depends(lambda: tool_service)
):
    """
    Get a specific Tool by its ID.
    """
    db_tool = service.get_tool_by_id(tool_id=tool_id)
    if db_tool is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")
    return db_tool

@router.get("/", response_model=List[Tool])
def list_tools(
    skip: int = 0,
    limit: int = 100,
    service: ToolService = Depends(lambda: tool_service)
):
    """
    Retrieve a list of Tools.
    """
    return service.list_tools(skip=skip, limit=limit)

@router.put("/{tool_id}", response_model=Tool)
def update_tool(
    tool_id: str,
    tool_in: ToolUpdate,
    service: ToolService = Depends(lambda: tool_service)
):
    """
    Update an existing Tool.
    """
    updated_tool = service.update_tool(tool_id=tool_id, tool_update=tool_in)
    if updated_tool is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")
    return updated_tool

@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tool(
    tool_id: str,
    service: ToolService = Depends(lambda: tool_service)
):
    """
    Delete a Tool.
    """
    deleted = service.delete_tool(tool_id=tool_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")
    return
