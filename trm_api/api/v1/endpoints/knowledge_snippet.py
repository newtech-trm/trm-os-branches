
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from trm_api.models.knowledge_snippet import KnowledgeSnippet, KnowledgeSnippetCreate, KnowledgeSnippetUpdate
from trm_api.services.knowledge_snippet_service import knowledge_snippet_service, KnowledgeSnippetService
from trm_api.adapters import adapt_datetime_response
from trm_api.adapters.decorators import adapt_response

router = APIRouter()

@router.post("/", response_model=None, status_code=status.HTTP_201_CREATED)
@adapt_datetime_response()
async def create_knowledge_snippet(
    snippet_in: KnowledgeSnippetCreate,
    service: KnowledgeSnippetService = Depends(lambda: knowledge_snippet_service)
):
    """
    Create a new Knowledge Snippet.
    """
    logging.info(f"Creating new knowledge snippet: {snippet_in.model_dump_json(exclude_unset=True)}")
    return service.create_snippet(snippet_create=snippet_in)

@router.get("/{snippet_id}", response_model=None)
@adapt_datetime_response()
async def get_knowledge_snippet(
    snippet_id: str,
    service: KnowledgeSnippetService = Depends(lambda: knowledge_snippet_service)
):
    """
    Get a specific Knowledge Snippet by its ID.
    """
    logging.info(f"Retrieving knowledge snippet with ID: {snippet_id}")
    db_snippet = service.get_snippet_by_id(snippet_id=snippet_id)
    if db_snippet is None:
        logging.warning(f"Knowledge snippet not found: {snippet_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge Snippet not found")
    return db_snippet

@router.get("/", response_model=None)
@adapt_datetime_response(response_item_key="items")
async def list_knowledge_snippets(
    skip: int = 0,
    limit: int = 100,
    service: KnowledgeSnippetService = Depends(lambda: knowledge_snippet_service)
):
    """
    Retrieve a list of Knowledge Snippets.
    """
    logging.info(f"Listing knowledge snippets with skip={skip}, limit={limit}")
    snippets = service.list_snippets(skip=skip, limit=limit)
    return {"items": snippets, "total": len(snippets), "skip": skip, "limit": limit}

@router.put("/{snippet_id}", response_model=None)
@adapt_datetime_response()
async def update_knowledge_snippet(
    snippet_id: str,
    snippet_in: KnowledgeSnippetUpdate,
    service: KnowledgeSnippetService = Depends(lambda: knowledge_snippet_service)
):
    """
    Update an existing Knowledge Snippet.
    """
    logging.info(f"Updating knowledge snippet {snippet_id}: {snippet_in.model_dump_json(exclude_unset=True)}")
    updated_snippet = service.update_snippet(snippet_id=snippet_id, snippet_update=snippet_in)
    if updated_snippet is None:
        logging.warning(f"Knowledge snippet not found for update: {snippet_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge Snippet not found")
    return updated_snippet

@router.delete("/{snippet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_snippet(
    snippet_id: str,
    service: KnowledgeSnippetService = Depends(lambda: knowledge_snippet_service)
):
    """
    Delete a Knowledge Snippet.
    """
    logging.info(f"Deleting knowledge snippet: {snippet_id}")
    deleted = service.delete_snippet(snippet_id=snippet_id)
    if not deleted:
        logging.warning(f"Knowledge snippet not found for deletion: {snippet_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge Snippet not found")
    return
