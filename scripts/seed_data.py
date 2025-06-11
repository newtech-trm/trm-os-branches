#!/usr/bin/env python
# coding: utf-8

"""
This script seeds the TRM-OS database with initial data.
It creates sample entities (Users, Projects, Teams, etc.) and the relationships between them
by calling the live API endpoints.

Prerequisites:
- The FastAPI server must be running.
- The required libraries (requests, rich) must be installed:
  pip install requests rich
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

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8000/api/v1"
console = Console()

# --- Sample Data ---
USERS_DATA = [
    {"email": "ada.lovelace@example.com", "fullName": "Ada Lovelace"},
    {"email": "grace.hopper@example.com", "fullName": "Grace Hopper"},
    {"email": "alan.turing@example.com", "fullName": "Alan Turing"},
]

TEAMS_DATA = [
    {"name": "Core Platform Team", "description": "Responsible for the core TRM-OS infrastructure."},
    {"name": "AI Agents Guild", "description": "Focuses on developing and improving autonomous agents."},
]

PROJECTS_DATA = [
    {"title": "Q3 Ontology Refinement", "description": "Refine and expand the core ontology based on Q2 learnings.", "status": "in_progress"},
    {"title": "Agent Collaboration MVP", "description": "Develop the minimum viable product for agent-to-agent collaboration.", "status": "not_started"},
]

# --- Helper Functions ---

def clear_database():
    """Connects to Neo4j and deletes all nodes and relationships."""
    console.rule("[bold red]Clearing Database[/bold red]")
    try:
        driver = get_driver()
        with driver.session() as session:
            # This query deletes all nodes and their relationships
            session.execute_write(lambda tx: tx.run("MATCH (n) DETACH DELETE n"))
        console.print("✅ Database cleared successfully.")
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        # Exit if we can't clear the DB, as it will lead to inconsistent state
        exit(1)

def _create_relationship_request(endpoint: str, description: str) -> dict:
    """Helper to send POST request for creating a relationship."""
    try:
        response = requests.post(f"{BASE_URL}{endpoint}")
        response.raise_for_status()
        console.print(f"✅ [green]Successfully created relationship:[/green] {description}")
        return response.json()
    except requests.exceptions.RequestException as e:
        console.print(f"❌ [bold red]Error creating relationship {description}:[/bold red] {e}")
        return None

def _post_request(endpoint: str, data: dict, description: str) -> dict:
    """Helper to send POST request and handle response."""
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        console.print(f"✅ [green]Successfully created {description}:[/green] {data.get('fullName') or data.get('name') or data.get('title')}")
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        console.print(f"❌ [bold red]Error creating {description}:[/bold red] {http_err}")
        # Cố gắng in chi tiết lỗi từ response của server
        try:
            error_details = http_err.response.json()
            console.print(f"[red]Server Response:[/red] {error_details}")
        except ValueError:
            console.print(f"[red]Server Response (non-JSON):[/red] {http_err.response.text}")
        return None
    except requests.exceptions.RequestException as req_err:
        console.print(f"❌ [bold red]Error creating {description} (Request failed):[/bold red] {req_err}")
        return None

def health_check(retries=5, delay=2):
    """Checks if the API is running, with a retry mechanism."""
    base_url = "http://127.0.0.1:8000"
    console.print("Pinging API for health check...", style="bold blue")
    for i in range(retries):
        try:
            response = requests.get(f"{base_url}/")
            response.raise_for_status()
            console.print("✅ [green]API is up and running! Let's start seeding.[/green]")
            return True
        except requests.exceptions.RequestException as e:
            console.print(f"Attempt {i + 1}/{retries} failed. Retrying in {delay}s...", style="yellow")
            time.sleep(delay)

    console.print(f"❌ [bold red]API is not accessible at {base_url} after {retries} attempts. Please start the server first.[/bold red]")
    return False

def create_users() -> list:
    """Creates users from the sample data."""
    console.rule("[bold blue]Step 1: Creating Users[/bold blue]")
    created_users = []
    for user_data in USERS_DATA:
        created_user = _post_request("/users/", user_data, "User")
        if created_user:
            created_users.append(created_user)
    return created_users

def create_teams() -> list:
    """Creates teams from the sample data."""
    console.rule("[bold blue]Step 2: Creating Teams[/bold blue]")
    created_teams = []
    for team_data in TEAMS_DATA:
        created_team = _post_request("/teams/", team_data, "Team")
        if created_team:
            created_teams.append(created_team)
    return created_teams

def create_projects() -> list:
    """Creates projects from the sample data."""
    console.rule("[bold blue]Step 3: Creating Projects[/bold blue]")
    created_projects = []
    for project_data in PROJECTS_DATA:
        created_project = _post_request("/projects/", project_data, "Project")
        if created_project:
            created_projects.append(created_project)
    return created_projects

def create_relationships(users: list, teams: list, projects: list) -> int:
    """Creates relationships between the existing entities."""
    console.rule("[bold blue]Step 4: Weaving the Web of Relationships[/bold blue]")
    relationships_created_count = 0

    # --- Assign Members to Teams ---
    # Ada & Grace -> Core Platform Team
    # Alan & Grace -> AI Agents Guild
    team_assignments = {
        "Core Platform Team": ["Ada Lovelace", "Grace Hopper"],
        "AI Agents Guild": ["Alan Turing", "Grace Hopper"]
    }
    for team_name, member_names in team_assignments.items():
        team = next((t for t in teams if t['name'] == team_name), None)
        if not team:
            continue
        for member_name in member_names:
            user = next((u for u in users if u['fullName'] == member_name), None)
            if user:
                endpoint = f"/teams/{team['teamId']}/add-member/{user['userId']}"
                desc = f"{user['fullName']} -> HAS_MEMBER -> {team['name']}"
                if _create_relationship_request(endpoint, desc):
                    relationships_created_count += 1

    # --- Assign Participants to Projects ---
    # Ada & Alan -> Q3 Ontology Refinement
    # Grace -> Agent Collaboration MVP
    project_assignments = {
        "Q3 Ontology Refinement": ["Ada Lovelace", "Alan Turing"],
        "Agent Collaboration MVP": ["Grace Hopper"]
    }
    for project_title, participant_names in project_assignments.items():
        project = next((p for p in projects if p['title'] == project_title), None)
        if not project:
            continue
        for participant_name in participant_names:
            user = next((u for u in users if u['fullName'] == participant_name), None)
            if user:
                endpoint = f"/projects/{project['projectId']}/add-participant/{user['userId']}"
                desc = f"{user['fullName']} -> HAS_PARTICIPANT -> {project['title']}"
                if _create_relationship_request(endpoint, desc):
                    relationships_created_count += 1
    
    return relationships_created_count

# --- Main Seeding Logic ---
def main():
    console.rule("[bold cyan]🚀 Starting TRM-OS Database Seeding 🚀[/bold cyan]")
    clear_database()

    if not health_check():
        console.rule("[bold red]Seeding Aborted[/bold red]")
        return

    # --- Create Entities ---
    users = create_users()
    teams = create_teams()
    projects = create_projects()

    if not users or not teams or not projects:
        console.print("Initial entity creation failed. Aborting further seeding.", style="bold red")
        return

    # --- Create Relationships ---
    relationships_count = create_relationships(users, teams, projects)

    # --- Summary ---
    console.rule("[bold blue]Summary of Seeding[/bold blue]")
    table = Table(title="Created Items")
    table.add_column("Item Type", justify="right", style="cyan", no_wrap=True)
    table.add_column("Count", justify="center", style="magenta")
    table.add_row("Users", str(len(users)))
    table.add_row("Teams", str(len(teams)))
    table.add_row("Projects", str(len(projects)))
    table.add_row("Relationships", str(relationships_count))
    console.print(table)

    console.rule("[bold green]✅ Seeding Completed Successfully ✅[/bold green]")

if __name__ == "__main__":
    main()
