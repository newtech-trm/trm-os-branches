from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from trm_api.models.agent import Agent, AgentCreate, AgentUpdate
from trm_api.services.agent_service import agent_service, AgentService

router = APIRouter()

@router.post("/", response_model=Agent, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_in: AgentCreate,
    service: AgentService = Depends(lambda: agent_service)
):
    """
    Create a new Agent.
    """
    return await service.create_agent(agent_create=agent_in)

@router.get("/{agent_id}", response_model=Agent)
async def get_agent(
    agent_id: str,
    service: AgentService = Depends(lambda: agent_service)
):
    """
    Get a specific Agent by its ID.
    """
    db_agent = await service.get_agent_by_id(agent_id=agent_id)
    if db_agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return db_agent

@router.get("/", response_model=List[Agent])
async def list_agents(
    skip: int = 0,
    limit: int = 100,
    service: AgentService = Depends(lambda: agent_service)
):
    """
    Retrieve a list of Agents.
    """
    return await service.list_agents(skip=skip, limit=limit)

@router.put("/{agent_id}", response_model=Agent)
async def update_agent(
    agent_id: str,
    agent_in: AgentUpdate,
    service: AgentService = Depends(lambda: agent_service)
):
    """
    Update an existing Agent.
    """
    updated_agent = await service.update_agent(agent_id=agent_id, agent_update=agent_in)
    if updated_agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return updated_agent

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    service: AgentService = Depends(lambda: agent_service)
):
    """
    Delete an Agent.
    """
    deleted = await service.delete_agent(agent_id=agent_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return
