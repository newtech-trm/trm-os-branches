#!/usr/bin/env python
# coding: utf-8

"""
Script để bơm dữ liệu thực tế cho KnowledgeSnippet và các relationship liên quan.
Đây là phần bổ sung cho script seed_data.py ban đầu, tập trung vào entity KnowledgeSnippet còn thiếu.

Prerequisites:
- API server phải đang chạy trên cổng 8000
- Neo4j đã kết nối
"""

import requests
import uuid
import time
import sys
import os

# Add the project root to the Python path to allow imports from trm_api
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import List, Dict, Any
from trm_api.db.session import get_driver
from rich.console import Console
from rich.table import Table
from datetime import datetime, timedelta

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8000/api/v1"
console = Console()

# --- Sample Data cho KnowledgeSnippet ---
KNOWLEDGE_SNIPPETS_DATA = [
    {
        "title": "Hướng dẫn thiết kế ontology V3.2",
        "content": "Tài liệu hướng dẫn chi tiết về thiết kế và triển khai ontology V3.2, bao gồm các entity và relationship chính theo chuẩn TRM.",
        "tags": ["ontology", "documentation", "design", "v3.2"],
        "source": "internal",
        "knowledgeType": "guide",
        "createdDate": (datetime.now() - timedelta(days=45)).isoformat()
    },
    {
        "title": "Neo4j Best Practices cho TRM",
        "content": "Tổng hợp các best practice khi làm việc với Neo4j và Cypher query trong dự án TRM, bao gồm cả mẫu query phức tạp và tối ưu hóa.",
        "tags": ["neo4j", "cypher", "best-practices", "optimization"],
        "source": "internal",
        "knowledgeType": "reference",
        "createdDate": (datetime.now() - timedelta(days=30)).isoformat()
    },
    {
        "title": "Chiến lược kiểm thử ontology",
        "content": "Phương pháp và chiến lược kiểm thử ontology toàn diện, bao gồm unit test, integration test và end-to-end validation.",
        "tags": ["testing", "validation", "ontology", "automation"],
        "source": "internal",
        "knowledgeType": "methodology",
        "createdDate": (datetime.now() - timedelta(days=15)).isoformat()
    },
    {
        "title": "FastAPI trong ứng dụng TRM",
        "content": "Hướng dẫn sử dụng FastAPI trong TRM API, bao gồm các pattern, dependency injection, và tích hợp với Neo4j.",
        "tags": ["fastapi", "api", "python", "backend"],
        "source": "internal",
        "knowledgeType": "tutorial",
        "createdDate": (datetime.now() - timedelta(days=60)).isoformat()
    },
    {
        "title": "AI Agent Ontology",
        "content": "Đặc tả và thiết kế cho phần ontology liên quan đến AI Agent, bao gồm các entity, relationship và use case.",
        "tags": ["ai", "agent", "ontology", "automation"],
        "source": "internal",
        "knowledgeType": "specification",
        "createdDate": (datetime.now() - timedelta(days=90)).isoformat()
    }
]

# --- Helper Functions ---

def _post_request(endpoint: str, data: dict, description: str) -> dict:
    """Helper to send POST request and handle response."""
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        console.print(f"✅ [green]Successfully created {description}:[/green] {data.get('title') or data.get('name')}")
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        console.print(f"❌ [bold red]Error creating {description}:[/bold red] {http_err}")
        # In chi tiết lỗi từ response của server
        try:
            error_details = http_err.response.json()
            console.print(f"[red]Server Response:[/red] {error_details}")
        except ValueError:
            console.print(f"[red]Server Response (non-JSON):[/red] {http_err.response.text}")
        return None
    except requests.exceptions.RequestException as req_err:
        console.print(f"❌ [bold red]Error creating {description} (Request failed):[/bold red] {req_err}")
        return None

def _create_relationship_request(endpoint: str, description: str, data=None) -> dict:
    """Helper to send POST request for creating a relationship."""
    try:
        if data:
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        else:
            response = requests.post(f"{BASE_URL}{endpoint}")
        response.raise_for_status()
        console.print(f"✅ [green]Successfully created relationship:[/green] {description}")
        return response.json()
    except requests.exceptions.RequestException as e:
        console.print(f"❌ [bold red]Error creating relationship {description}:[/bold red] {e}")
        return None

def health_check(retries=5, delay=2):
    """Checks if the API is running, with a retry mechanism."""
    console.print("Checking API health...", style="bold blue")
    
    for attempt in range(retries):
        try:
            response = requests.get(f"{BASE_URL}/users/")
            if response.status_code == 200:
                console.print("✅ [green]API server is running![/green]")
                return True
            else:
                console.print(f"⚠️ API responded with status code: {response.status_code}. Retrying in {delay} seconds...")
        except requests.exceptions.RequestException:
            if attempt < retries - 1:
                console.print(f"⚠️ API server not responding. Retrying in {delay} seconds... (Attempt {attempt + 1}/{retries})")
                time.sleep(delay)
            else:
                console.print("❌ [bold red]Could not connect to API server after multiple attempts.[/bold red]")
                console.print("Make sure the API server is running on http://127.0.0.1:8000", style="yellow")
                return False
    
    return False

def create_knowledge_snippets() -> list:
    """Creates knowledge snippets from the sample data."""
    console.rule("[bold blue]Creating Knowledge Snippets[/bold blue]")
    created_snippets = []
    for snippet_data in KNOWLEDGE_SNIPPETS_DATA:
        created_snippet = _post_request("/knowledge-snippets/", snippet_data, "Knowledge Snippet")
        if created_snippet:
            created_snippets.append(created_snippet)
    return created_snippets

def get_users() -> list:
    """Gets existing users from the API."""
    console.print("Getting existing users...", style="bold blue")
    try:
        response = requests.get(f"{BASE_URL}/users/")
        response.raise_for_status()
        users = response.json()
        if users:
            console.print(f"✅ [green]Found {len(users)} existing users.[/green]")
            return users
        else:
            console.print("⚠️ No existing users found. Please run seed_data.py first.")
            return []
    except requests.exceptions.RequestException as e:
        console.print(f"❌ [bold red]Error getting users:[/bold red] {e}")
        return []

def get_events() -> list:
    """Gets existing events from the API."""
    console.print("Getting existing events...", style="bold blue")
    try:
        response = requests.get(f"{BASE_URL}/events/")
        response.raise_for_status()
        events = response.json()
        if events:
            console.print(f"✅ [green]Found {len(events)} existing events.[/green]")
            return events
        else:
            console.print("⚠️ No existing events found. Please run seed_events_data.py first.")
            return []
    except requests.exceptions.RequestException as e:
        console.print(f"❌ [bold red]Error getting events:[/bold red] {e}")
        return []

def get_projects() -> list:
    """Gets existing projects from the API."""
    console.print("Getting existing projects...", style="bold blue")
    try:
        response = requests.get(f"{BASE_URL}/projects/")
        response.raise_for_status()
        projects = response.json()
        if projects:
            console.print(f"✅ [green]Found {len(projects)} existing projects.[/green]")
            return projects
        else:
            console.print("⚠️ No existing projects found. Please run seed_data.py first.")
            return []
    except requests.exceptions.RequestException as e:
        console.print(f"❌ [bold red]Error getting projects:[/bold red] {e}")
        return []

def create_knowledge_relationships(snippets: list, users: list, events: list, projects: list) -> int:
    """Creates relationships between knowledge snippets and other entities."""
    console.rule("[bold blue]Creating Knowledge Relationships[/bold blue]")
    relationships_created_count = 0

    if not snippets or not users:
        console.print("Missing required entities. Cannot create knowledge relationships.", style="bold red")
        return relationships_created_count

    # --- Link Knowledge to Users (AUTHORED_BY) ---
    # Each knowledge snippet is authored by one user
    for i, snippet in enumerate(snippets):
        user = users[i % len(users)]
        endpoint = f"/knowledge-snippets/{snippet['knowledgeSnippetId']}/authored-by/{user['userId']}"
        rel_data = {
            "date": datetime.now().isoformat(),
            "notes": f"Knowledge snippet được tạo bởi {user['fullName']}"
        }
        desc = f"KnowledgeSnippet:{snippet['title']} -> AUTHORED_BY -> User:{user['fullName']}"
        if _create_relationship_request(endpoint, desc, rel_data):
            relationships_created_count += 1

    # --- Link Events to Knowledge (GENERATES_KNOWLEDGE) ---
    if events:
        for i, event in enumerate(events):
            if i >= len(snippets):
                break
                
            snippet = snippets[i]
            endpoint = f"/events/{event['eventId']}/generates-knowledge/{snippet['knowledgeSnippetId']}"
            rel_data = {
                "date": datetime.now().isoformat(),
                "context": f"Knowledge được tạo ra từ event {event.get('title', '')}",
                "relevanceScore": 0.85
            }
            desc = f"Event:{event.get('title', '')} -> GENERATES_KNOWLEDGE -> KnowledgeSnippet:{snippet['title']}"
            if _create_relationship_request(endpoint, desc, rel_data):
                relationships_created_count += 1

    # --- Link Knowledge to Projects (RELATES_TO) ---
    if projects:
        for i, snippet in enumerate(snippets):
            project = projects[i % len(projects)]
            endpoint = f"/knowledge-snippets/{snippet['knowledgeSnippetId']}/relates-to/{project['projectId']}"
            rel_data = {
                "relevance": "high",
                "notes": f"Knowledge snippet liên quan đến project {project['title']}"
            }
            desc = f"KnowledgeSnippet:{snippet['title']} -> RELATES_TO -> Project:{project['title']}"
            if _create_relationship_request(endpoint, desc, rel_data):
                relationships_created_count += 1

    return relationships_created_count

def main():
    console.rule("[bold cyan]🚀 Seeding Knowledge Snippets and Relationships 🚀[/bold cyan]")

    if not health_check():
        console.rule("[bold red]Seeding Aborted[/bold red]")
        return

    # --- Create Knowledge Snippets ---
    snippets = create_knowledge_snippets()

    # --- Get existing entities ---
    users = get_users()
    events = get_events()
    projects = get_projects()

    if not snippets or not users:
        console.print("Missing required entities. Aborting further seeding.", style="bold red")
        return

    # --- Create Knowledge Relationships ---
    relationships_count = create_knowledge_relationships(snippets, users, events, projects)

    # --- Summary ---
    console.rule("[bold blue]Summary of Seeding[/bold blue]")
    table = Table(title="Created Items")
    table.add_column("Item Type", justify="right", style="cyan", no_wrap=True)
    table.add_column("Count", justify="center", style="magenta")
    table.add_row("Knowledge Snippets", str(len(snippets)))
    table.add_row("Knowledge Relationships", str(relationships_count))
    console.print(table)

    console.rule("[bold green]✅ Knowledge Snippet Seeding Completed Successfully ✅[/bold green]")

if __name__ == "__main__":
    main()
