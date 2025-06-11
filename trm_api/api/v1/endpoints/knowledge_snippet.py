from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from trm_api.models.knowledge_snippet import KnowledgeSnippet, KnowledgeSnippetCreate, KnowledgeSnippetUpdate
from trm_api.services.knowledge_snippet_service import knowledge_snippet_service, KnowledgeSnippetService

router = APIRouter()

@router.post("/", response_model=KnowledgeSnippet, status_code=status.HTTP_201_CREATED)
def create_knowledge_snippet(
    snippet_in: KnowledgeSnippetCreate,
    service: KnowledgeSnippetService = Depends(lambda: knowledge_snippet_service)
):
    """
    Create a new Knowledge Snippet.
    """
    return service.create_knowledge_snippet(snippet_create=snippet_in)

@router.get("/{snippet_id}", response_model=KnowledgeSnippet)
def get_knowledge_snippet(
    snippet_id: str,
    service: KnowledgeSnippetService = Depends(lambda: knowledge_snippet_service)
):
    """
    Get a specific Knowledge Snippet by its ID.
    """
    db_snippet = service.get_knowledge_snippet_by_id(snippet_id=snippet_id)
    if db_snippet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge Snippet not found")
    return db_snippet

@router.get("/", response_model=List[KnowledgeSnippet])
def list_knowledge_snippets(
    skip: int = 0,
    limit: int = 100,
    service: KnowledgeSnippetService = Depends(lambda: knowledge_snippet_service)
):
    """
    Retrieve a list of Knowledge Snippets.
    """
    return service.list_knowledge_snippets(skip=skip, limit=limit)

@router.put("/{snippet_id}", response_model=KnowledgeSnippet)
def update_knowledge_snippet(
    snippet_id: str,
    snippet_in: KnowledgeSnippetUpdate,
    service: KnowledgeSnippetService = Depends(lambda: knowledge_snippet_service)
):
    """
    Update an existing Knowledge Snippet.
    """
    updated_snippet = service.update_knowledge_snippet(snippet_id=snippet_id, snippet_update=snippet_in)
    if updated_snippet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge Snippet not found")
    return updated_snippet

@router.delete("/{snippet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge_snippet(
    snippet_id: str,
    service: KnowledgeSnippetService = Depends(lambda: knowledge_snippet_service)
):
    """
    Delete a Knowledge Snippet.
    """
    deleted = service.delete_knowledge_snippet(snippet_id=snippet_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge Snippet not found")
    return
