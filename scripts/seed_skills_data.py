#!/usr/bin/env python
# coding: utf-8

"""
Script để bơm dữ liệu thực tế cho GraphSkill và các relationship liên quan.
Đây là phần bổ sung cho script seed_data.py ban đầu, tập trung vào entity GraphSkill còn thiếu.

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
from datetime import datetime

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8000/api/v1"
console = Console()

# --- Sample Data cho GraphSkill ---
SKILLS_DATA = [
    {
        "name": "Neo4j",
        "description": "Kiến thức và kỹ năng về cơ sở dữ liệu đồ thị Neo4j",
        "category": "Database",
        "level": 5
    },
    {
        "name": "Ontology Design",
        "description": "Thiết kế và phát triển ontology",
        "category": "Knowledge Engineering",
        "level": 4
    },
    {
        "name": "FastAPI",
        "description": "Framework API hiệu suất cao cho Python",
        "category": "Backend",
        "level": 4
    },
    {
        "name": "Python",
        "description": "Ngôn ngữ lập trình Python",
        "category": "Programming",
        "level": 5
    },
    {
        "name": "Graph Theory",
        "description": "Lý thuyết đồ thị và các thuật toán liên quan",
        "category": "Computer Science",
        "level": 3
    }
]

# --- Helper Functions ---

def _post_request(endpoint: str, data: dict, description: str) -> dict:
    """Helper to send POST request and handle response."""
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        console.print(f"✅ [green]Successfully created {description}:[/green] {data.get('name') or data.get('title')}")
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

def create_skills() -> list:
    """Creates skills from the sample data."""
    console.rule("[bold blue]Creating Skills[/bold blue]")
    created_skills = []
    for skill_data in SKILLS_DATA:
        created_skill = _post_request("/skills/", skill_data, "Skill")
        if created_skill:
            created_skills.append(created_skill)
    return created_skills

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

def create_skill_relationships(skills: list, users: list, projects: list) -> int:
    """Creates relationships between skills and other entities."""
    console.rule("[bold blue]Creating Skill Relationships[/bold blue]")
    relationships_created_count = 0

    if not skills or not users:
        console.print("Missing required entities. Cannot create skill relationships.", style="bold red")
        return relationships_created_count

    # --- Assign Skills to Users (HAS_SKILL) ---
    # Distribute skills among users
    for i, user in enumerate(users):
        # Lấy 2-3 skill cho mỗi user
        user_skills = skills[i:i+3]
        if i >= len(skills):
            break

        for skill in user_skills:
            endpoint = f"/users/{user['userId']}/has-skill/{skill['skillId']}"
            rel_data = {
                "proficiencyLevel": skill['level'],
                "yearsExperience": i + 1,
                "notes": f"User {user['fullName']} có kinh nghiệm với {skill['name']}"
            }
            desc = f"User:{user['fullName']} -> HAS_SKILL -> Skill:{skill['name']}"
            if _create_relationship_request(endpoint, desc, rel_data):
                relationships_created_count += 1

    # --- Link Skills to Projects (REQUIRES_SKILL) ---
    # Distribute skills among projects
    for i, project in enumerate(projects):
        # Lấy 1-2 skill cho mỗi project
        project_skills = skills[i:i+2]
        if i >= len(skills):
            break

        for skill in project_skills:
            endpoint = f"/projects/{project['projectId']}/requires-skill/{skill['skillId']}"
            rel_data = {
                "requiredLevel": skill['level'] - 1 if skill['level'] > 1 else 1,
                "importance": "high" if skill['level'] >= 4 else "medium",
                "notes": f"Project {project['title']} cần kỹ năng {skill['name']}"
            }
            desc = f"Project:{project['title']} -> REQUIRES_SKILL -> Skill:{skill['name']}"
            if _create_relationship_request(endpoint, desc, rel_data):
                relationships_created_count += 1

    return relationships_created_count

def main():
    console.rule("[bold cyan]🚀 Seeding Skills and Relationships 🚀[/bold cyan]")

    if not health_check():
        console.rule("[bold red]Seeding Aborted[/bold red]")
        return

    # --- Create Skills ---
    skills = create_skills()

    # --- Get existing entities ---
    users = get_users()
    projects = get_projects()

    if not skills or not users:
        console.print("Missing required entities. Aborting further seeding.", style="bold red")
        return

    # --- Create Skill Relationships ---
    relationships_count = create_skill_relationships(skills, users, projects)

    # --- Summary ---
    console.rule("[bold blue]Summary of Seeding[/bold blue]")
    table = Table(title="Created Items")
    table.add_column("Item Type", justify="right", style="cyan", no_wrap=True)
    table.add_column("Count", justify="center", style="magenta")
    table.add_row("Skills", str(len(skills)))
    table.add_row("Skill Relationships", str(relationships_count))
    console.print(table)

    console.rule("[bold green]✅ Skill Seeding Completed Successfully ✅[/bold green]")

if __name__ == "__main__":
    main()
