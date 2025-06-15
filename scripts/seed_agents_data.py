#!/usr/bin/env python
# coding: utf-8

"""
Script để bơm dữ liệu thực tế cho Agent, Action và các relationship liên quan.
Đây là phần bổ sung cuối cùng cho script seed_data.py ban đầu, tập trung vào entity Agent và Action còn thiếu.

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

# --- Sample Data cho Agent ---
AGENTS_DATA = [
    {
        "name": "OntologyValidator",
        "description": "Agent chuyên kiểm tra và xác thực ontology V3.2",
        "agentType": "validation",
        "status": "active",
        "capabilities": ["ontology_analysis", "graph_validation", "data_verification"]
    },
    {
        "name": "DataImporter",
        "description": "Agent phụ trách import và bơm dữ liệu vào Neo4j",
        "agentType": "data",
        "status": "active",
        "capabilities": ["data_import", "database_seeding", "entity_creation"]
    },
    {
        "name": "RelationshipManager",
        "description": "Agent quản lý và kiểm thử relationship giữa các entity",
        "agentType": "management",
        "status": "active",
        "capabilities": ["relationship_testing", "graph_traversal", "integrity_checking"]
    },
    {
        "name": "OntologyExplorer",
        "description": "Agent khám phá và phân tích ontology",
        "agentType": "analysis",
        "status": "active",
        "capabilities": ["graph_exploration", "pattern_recognition", "structure_analysis"]
    }
]

# --- Sample Data cho Action ---
ACTIONS_DATA = [
    {
        "name": "ValidateEntity",
        "description": "Kiểm tra entity có tuân thủ schema và ontology V3.2 không",
        "actionType": "validation",
        "parameters": {"entityType": "string", "validateSchema": "boolean", "recursive": "boolean"}
    },
    {
        "name": "ImportData",
        "description": "Nhập dữ liệu vào Neo4j cho một entity cụ thể",
        "actionType": "data",
        "parameters": {"dataSource": "string", "entityType": "string", "batchSize": "number"}
    },
    {
        "name": "CreateRelationship",
        "description": "Tạo relationship giữa hai entity",
        "actionType": "create",
        "parameters": {"sourceId": "string", "targetId": "string", "relationshipType": "string"}
    },
    {
        "name": "AnalyzeGraph",
        "description": "Phân tích cấu trúc đồ thị và báo cáo kết quả",
        "actionType": "analysis",
        "parameters": {"depth": "number", "includeProperties": "boolean", "outputFormat": "string"}
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

def create_agents() -> list:
    """Creates agents from the sample data."""
    console.rule("[bold blue]Creating Agents[/bold blue]")
    created_agents = []
    for agent_data in AGENTS_DATA:
        created_agent = _post_request("/agents/", agent_data, "Agent")
        if created_agent:
            created_agents.append(created_agent)
    return created_agents

def create_actions() -> list:
    """Creates actions from the sample data."""
    console.rule("[bold blue]Creating Actions[/bold blue]")
    created_actions = []
    for action_data in ACTIONS_DATA:
        created_action = _post_request("/actions/", action_data, "Action")
        if created_action:
            created_actions.append(created_action)
    return created_actions

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

def get_tasks() -> list:
    """Gets existing tasks from the API."""
    console.print("Getting existing tasks...", style="bold blue")
    try:
        response = requests.get(f"{BASE_URL}/tasks/")
        response.raise_for_status()
        tasks = response.json()
        if tasks:
            console.print(f"✅ [green]Found {len(tasks)} existing tasks.[/green]")
            return tasks
        else:
            console.print("⚠️ No existing tasks found. Please run seed_tasks_data.py first.")
            return []
    except requests.exceptions.RequestException as e:
        console.print(f"❌ [bold red]Error getting tasks:[/bold red] {e}")
        return []

def create_agent_relationships(agents: list, actions: list, users: list, tasks: list) -> int:
    """Creates relationships between agents, actions, and other entities."""
    console.rule("[bold blue]Creating Agent Relationships[/bold blue]")
    relationships_created_count = 0

    if not agents or not actions:
        console.print("Missing required entities. Cannot create agent relationships.", style="bold red")
        return relationships_created_count

    # --- Link Agents to Actions (CAN_PERFORM) ---
    # Each agent can perform 1-2 actions
    for i, agent in enumerate(agents):
        # Select actions for each agent (custom mapping based on capabilities)
        agent_actions = []
        if "validation" in agent["agentType"]:
            agent_actions.extend([a for a in actions if a["actionType"] == "validation"])
        elif "data" in agent["agentType"]:
            agent_actions.extend([a for a in actions if a["actionType"] == "data"])
        else:
            # Fallback to cyclic assignment
            start_idx = i % len(actions)
            agent_actions = actions[start_idx:start_idx+2]
            if start_idx + 2 > len(actions):
                agent_actions.extend(actions[:(start_idx+2) % len(actions)])

        for action in agent_actions[:2]:  # Limit to 2 actions per agent
            endpoint = f"/agents/{agent['agentId']}/can-perform/{action['actionId']}"
            rel_data = {
                "proficiency": "high" if agent["agentType"] == action["actionType"] else "medium",
                "notes": f"Agent {agent['name']} can perform action {action['name']}"
            }
            desc = f"Agent:{agent['name']} -> CAN_PERFORM -> Action:{action['name']}"
            if _create_relationship_request(endpoint, desc, rel_data):
                relationships_created_count += 1

    # --- Link Agents to Users (MANAGED_BY) ---
    # Each agent is managed by a user
    if users:
        for i, agent in enumerate(agents):
            user = users[i % len(users)]
            endpoint = f"/agents/{agent['agentId']}/managed-by/{user['userId']}"
            rel_data = {
                "role": "owner",
                "since": datetime.now().isoformat(),
                "notes": f"Agent {agent['name']} được quản lý bởi {user['fullName']}"
            }
            desc = f"Agent:{agent['name']} -> MANAGED_BY -> User:{user['fullName']}"
            if _create_relationship_request(endpoint, desc, rel_data):
                relationships_created_count += 1

    # --- Link Agents to Tasks (EXECUTES_TASK) ---
    # Some agents execute tasks
    if tasks:
        # Map specific agent types to relevant tasks
        for i, task in enumerate(tasks):
            if i >= len(agents):
                break
                
            agent = agents[i]
            endpoint = f"/agents/{agent['agentId']}/executes-task/{task['taskId']}"
            rel_data = {
                "status": "in_progress",
                "startDate": datetime.now().isoformat(),
                "notes": f"Agent {agent['name']} đang thực hiện task {task['name']}"
            }
            desc = f"Agent:{agent['name']} -> EXECUTES_TASK -> Task:{task['name']}"
            if _create_relationship_request(endpoint, desc, rel_data):
                relationships_created_count += 1

    return relationships_created_count

def main():
    console.rule("[bold cyan]🚀 Seeding Agents, Actions and Relationships 🚀[/bold cyan]")

    if not health_check():
        console.rule("[bold red]Seeding Aborted[/bold red]")
        return

    # --- Create Agents and Actions ---
    agents = create_agents()
    actions = create_actions()

    # --- Get existing entities ---
    users = get_users()
    tasks = get_tasks()

    if not agents or not actions:
        console.print("Missing required entities. Aborting further seeding.", style="bold red")
        return

    # --- Create Relationships ---
    relationships_count = create_agent_relationships(agents, actions, users, tasks)

    # --- Summary ---
    console.rule("[bold blue]Summary of Seeding[/bold blue]")
    table = Table(title="Created Items")
    table.add_column("Item Type", justify="right", style="cyan", no_wrap=True)
    table.add_column("Count", justify="center", style="magenta")
    table.add_row("Agents", str(len(agents)))
    table.add_row("Actions", str(len(actions)))
    table.add_row("Agent Relationships", str(relationships_count))
    console.print(table)

    console.rule("[bold green]✅ Agents and Actions Seeding Completed Successfully ✅[/bold green]")

if __name__ == "__main__":
    main()
