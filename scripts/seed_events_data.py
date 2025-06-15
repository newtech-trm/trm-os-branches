#!/usr/bin/env python
# coding: utf-8

"""
Script để bơm dữ liệu thực tế cho Event và các relationship liên quan.
Đây là phần bổ sung cho script seed_data.py ban đầu, tập trung vào entity Event còn thiếu.

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

# --- Sample Data cho Event ---
EVENTS_DATA = [
    {
        "title": "Khởi động dự án ontology V3.2",
        "description": "Buổi họp khởi động dự án triển khai ontology V3.2",
        "eventType": "meeting",
        "startDate": (datetime.now() - timedelta(days=30)).isoformat(),
        "endDate": (datetime.now() - timedelta(days=30, hours=-1)).isoformat(),
        "status": "completed",
        "location": "Phòng họp 1"
    },
    {
        "title": "Review tiến độ ontology",
        "description": "Họp đánh giá tiến độ triển khai các entity và relationship của ontology",
        "eventType": "meeting",
        "startDate": (datetime.now() - timedelta(days=15)).isoformat(),
        "endDate": (datetime.now() - timedelta(days=15, hours=-2)).isoformat(),
        "status": "completed",
        "location": "Online"
    },
    {
        "title": "Thảo luận strategy AI Agents",
        "description": "Thảo luận chiến lược phát triển AI agents dựa trên ontology",
        "eventType": "workshop",
        "startDate": (datetime.now() - timedelta(days=7)).isoformat(),
        "endDate": (datetime.now() - timedelta(days=7, hours=-4)).isoformat(),
        "status": "completed",
        "location": "Phòng họp 2"
    },
    {
        "title": "Sprint planning",
        "description": "Lập kế hoạch sprint mới tập trung vào ontology validation",
        "eventType": "meeting",
        "startDate": (datetime.now() - timedelta(days=3)).isoformat(),
        "endDate": (datetime.now() - timedelta(days=3, hours=-1)).isoformat(), 
        "status": "completed",
        "location": "Online"
    },
    {
        "title": "Kiểm tra kết quả validation",
        "description": "Đánh giá kết quả validation ontology và đề xuất cải thiện",
        "eventType": "review",
        "startDate": (datetime.now() + timedelta(days=3)).isoformat(),
        "endDate": (datetime.now() + timedelta(days=3, hours=2)).isoformat(),
        "status": "scheduled",
        "location": "Phòng họp 1"
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

def create_events() -> list:
    """Creates events from the sample data."""
    console.rule("[bold blue]Creating Events[/bold blue]")
    created_events = []
    for event_data in EVENTS_DATA:
        created_event = _post_request("/events/", event_data, "Event")
        if created_event:
            created_events.append(created_event)
    return created_events

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

def create_event_relationships(events: list, users: list, projects: list) -> int:
    """Creates relationships between events and other entities."""
    console.rule("[bold blue]Creating Event Relationships[/bold blue]")
    relationships_created_count = 0

    if not events or not users or not projects:
        console.print("Missing required entities. Cannot create event relationships.", style="bold red")
        return relationships_created_count

    # --- Link Users to Events (PARTICIPATES_IN) ---
    user_event_assignments = {}
    
    # Distribute users across events
    if len(users) > 0:
        for i, event in enumerate(events):
            # Assign 1-2 users to each event
            event_users = users[i % len(users):i % len(users) + 2]
            user_event_assignments[event['eventId']] = event_users
            
    for event_id, event_users in user_event_assignments.items():
        for user in event_users:
            endpoint = f"/users/{user['userId']}/participates-in-event/{event_id}"
            rel_data = {
                "role": "organizer" if user == event_users[0] else "participant",
                "notes": f"User {user['fullName']} tham gia event"
            }
            desc = f"User:{user['fullName']} -> PARTICIPATES_IN -> Event:{event_id}"
            if _create_relationship_request(endpoint, desc, rel_data):
                relationships_created_count += 1

    # --- Link Events to Projects (RELATED_TO_PROJECT) ---
    project_event_assignments = {}
    
    # Distribute events across projects
    if len(projects) > 0:
        for i, event in enumerate(events):
            project = projects[i % len(projects)]
            if project['projectId'] not in project_event_assignments:
                project_event_assignments[project['projectId']] = []
            project_event_assignments[project['projectId']].append(event)
            
    for project_id, project_events in project_event_assignments.items():
        for event in project_events:
            endpoint = f"/events/{event['eventId']}/related-to-project/{project_id}"
            rel_data = {
                "relationshipType": "planning" if "planning" in event['title'].lower() else "review",
                "notes": f"Event liên quan đến project {project_id}"
            }
            desc = f"Event:{event['title']} -> RELATED_TO_PROJECT -> Project:{project_id}"
            if _create_relationship_request(endpoint, desc, rel_data):
                relationships_created_count += 1

    # --- Link Events to generate KnowledgeSnippets (GENERATES_KNOWLEDGE) ---
    # Relationship này sẽ được tạo sau khi KnowledgeSnippet được tạo

    return relationships_created_count

def main():
    console.rule("[bold cyan]🚀 Seeding Events and Relationships 🚀[/bold cyan]")

    if not health_check():
        console.rule("[bold red]Seeding Aborted[/bold red]")
        return

    # --- Create Events ---
    events = create_events()

    # --- Get existing entities ---
    users = get_users()
    projects = get_projects()

    if not events or not users or not projects:
        console.print("Missing required entities. Aborting further seeding.", style="bold red")
        return

    # --- Create Event Relationships ---
    relationships_count = create_event_relationships(events, users, projects)

    # --- Summary ---
    console.rule("[bold blue]Summary of Seeding[/bold blue]")
    table = Table(title="Created Items")
    table.add_column("Item Type", justify="right", style="cyan", no_wrap=True)
    table.add_column("Count", justify="center", style="magenta")
    table.add_row("Events", str(len(events)))
    table.add_row("Event Relationships", str(relationships_count))
    console.print(table)

    console.rule("[bold green]✅ Event Seeding Completed Successfully ✅[/bold green]")

if __name__ == "__main__":
    main()
