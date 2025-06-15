#!/usr/bin/env python
# coding: utf-8

"""
Script để bơm dữ liệu Founder đặc biệt vào Neo4j theo đúng Ontology v3.2.
Founder là một InternalAgent đặc biệt, là nguồn phát động Recognition, định hướng triết lý, khởi tạo vòng lặp tiến hóa.

Prerequisites:
- API server phải đang chạy trên cổng 8000
- Neo4j đã kết nối
- Ontology v3.2 đã được cập nhật với định nghĩa Founder
"""

import requests
import uuid
import time
import sys
import os
from datetime import datetime, timedelta

# Add the project root to the Python path to allow imports from trm_api
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from trm_api.db.session import get_driver
from rich.console import Console
from rich.table import Table

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8001/api/v1"  # Updated to port 8001
console = Console()

# --- Sample Data cho Founder (InternalAgent đặc biệt) ---
FOUNDER_DATA = {
    "name": "TRM Founder",
    "purpose": "To initiate and embody the TRM vision, driving the evolution of the TRM Operating System.",
    "description": "Founder của TRM, người phát động Recognition đầu tiên, định hướng triết lý của hệ thống",
    "agent_type": "InternalAgent", # Phải là InternalAgent theo Ontology v3.2
    "status": "active",
    "capabilities": ["recognition", "vision_setting", "strategic_planning", "resource_allocation"],
    "job_title": "CEO",
    "department": "Management",
    "is_founder": True,  # Đánh dấu đây là Founder
    "founder_recognition_authority": True  # Có quyền tạo Recognition
}

# --- Các Resource, Project và Agent mà Founder sẽ có relationship ---
TEST_RESOURCES = [
    {
        "name": "Ontology v3.2 Documentation",
        "description": "Tài liệu định nghĩa chi tiết Ontology v3.2",
        "resourceType": "Knowledge",
        "status": "active",
        "details": {"format": "Markdown Document", "location": "docs/ontology_v3.2.md", "accessLevel": "internal"}
    },
    {
        "name": "TRM-OS Backend System",
        "description": "Hệ thống backend cho TRM-OS với Neo4j",
        "resourceType": "Tool",
        "status": "in_development",
        "details": {"tool_category": "Software Infrastructure", "version": "1.0", "access_url": "http://127.0.0.1:8000"}
    }
]

TEST_PROJECTS = [
    {
        "title": "Ontology v3.2 Implementation",
        "description": "Triển khai đầy đủ Ontology v3.2 vào hệ thống TRM-OS",
        "status": "active",
        "priority": 1
    },
    {
        "title": "AI Agent Framework Development",
        "description": "Phát triển framework cho Agent tương tác tự động với hệ thống",
        "status": "planned",
        "priority": 2
    }
]

TEST_AGENTS = [
    {
        "name": "AGE-System",
        "purpose": "To serve as the central Artificial Genesis Engine, coordinating system-wide operations and learning.",
        "description": "Artificial Genesis Engine - Hệ thống AI trung tâm của TRM-OS",
        "agent_type": "AGE",
        "status": "active",
        "capabilities": ["agent_coordination", "system_management", "learning", "event_processing"]
    },
    {
        "name": "RecognitionAgent",
        "purpose": "To identify and process Recognitions from various data sources, fueling the system's evolution.",
        "description": "Agent chuyên phát hiện Recognition từ dữ liệu và hoạt động",
        "agent_type": "AIAgent",
        "status": "active",
        "capabilities": ["pattern_recognition", "data_analysis", "recommendation"]
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

def _create_relationship_request(endpoint: str, description: str, data=None) -> bool:
    """Helper to send POST request for creating a relationship."""
    try:
        if data:
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        else:
            response = requests.post(f"{BASE_URL}{endpoint}")
            
        response.raise_for_status()  # Raise an exception for bad status codes
        console.print(f"🔗 [cyan]Successfully created relationship:[/cyan] {description}")
        return True
    except requests.exceptions.HTTPError as http_err:
        console.print(f"❌ [bold red]Error creating relationship {description}:[/bold red] {http_err}")
        # In chi tiết lỗi từ response của server
        try:
            error_details = http_err.response.json()
            console.print(f"[red]Server Response:[/red] {error_details}")
        except ValueError:
            console.print(f"[red]Server Response (non-JSON):[/red] {http_err.response.text}")
        return False

def health_check(retries=5, delay=2) -> bool:
    """Checks if the API is running, with a retry mechanism."""
    console.print("🔍 Checking if API is running...")
    # Lấy base URL không bao gồm /api/v1 để check health endpoint
    base_server_url = BASE_URL.split('/api/')[0]
    for attempt in range(retries):
        try:
            response = requests.get(f"{base_server_url}/health")
            if response.status_code == 200:
                console.print("✅ [green]API is running![/green]")
                return True
            else:
                console.print(f"⚠️ [yellow]API returned status code {response.status_code}[/yellow]")
        except requests.exceptions.ConnectionError:
            console.print(f"⚠️ [yellow]API not responding (attempt {attempt+1}/{retries}). Waiting {delay} seconds...[/yellow]")
            time.sleep(delay)
    
    console.print("❌ [bold red]API is not running. Please start the server first.[/bold red]")
    return False

def create_founder() -> dict:
    """Creates the Founder special InternalAgent."""
    console.print("\n🚀 Creating Founder (Special InternalAgent)...")
    response = _post_request("/agents", FOUNDER_DATA, "Founder")
    return response

def create_test_resources() -> list:
    """Creates test resources for relationships."""
    console.print("\n📦 Creating test resources...")
    resources = []
    for resource_data in TEST_RESOURCES:
        response = _post_request("/resources", resource_data, "Resource")
        if response:
            resources.append(response)
    return resources

def create_test_projects() -> list:
    """Creates test projects for relationships."""
    console.print("\n📋 Creating test projects...")
    projects = []
    for project_data in TEST_PROJECTS:
        response = _post_request("/projects", project_data, "Project")
        if response:
            projects.append(response)
    return projects

def create_test_agents() -> list:
    """Creates test agents for relationships."""
    console.print("\n🤖 Creating test agents...")
    agents = []
    for agent_data in TEST_AGENTS:
        response = _post_request("/agents", agent_data, "Agent")
        if response:
            agents.append(response)
    return agents

def create_founder_relationships(founder: dict, resources: list, projects: list, agents: list) -> int:
    """Creates relationships specific to the Founder role."""
    console.print("\n🔗 Creating Founder relationships...")
    relationships_created_count = 0
    
    # --- Founder RECOGNIZES Resources ---
    # Founder nhận diện giá trị và tiềm năng trong resources
    for resource in resources:
        endpoint = f"/agents/{founder['agentId']}/recognizes/{resource['resourceId']}"
        rel_data = {
            "recognitionDate": datetime.now().isoformat(),
            "valueRecognized": "Giá trị chiến lược cho sự phát triển của TRM-OS",
            "potentialUse": "Làm nền tảng cho các tính năng và workflow mới",
            "notes": f"Founder nhận diện giá trị trong {resource['name']}"
        }
        desc = f"Founder -> RECOGNIZES -> Resource:{resource['name']}"
        if _create_relationship_request(endpoint, desc, rel_data):
            relationships_created_count += 1
    
    # --- Founder APPROVES Projects ---
    # Founder phê duyệt và định hướng các dự án chiến lược
    for project in projects:
        endpoint = f"/agents/{founder['agentId']}/approves/{project['uid']}"
        rel_data = {
            "approvalDate": datetime.now().isoformat(),
            "priority": project['priority'],
            "strategicAlignment": "Alignment with TRM vision and mission",
            "notes": f"Founder phê duyệt dự án {project['name']}"
        }
        desc = f"Founder -> APPROVES -> Project:{project['name']}"
        if _create_relationship_request(endpoint, desc, rel_data):
            relationships_created_count += 1
    
    # --- Founder GUIDES Agents ---
    # Founder định hướng và quản lý các agent
    for agent in agents:
        endpoint = f"/agents/{founder['agentId']}/guides/{agent['agentId']}"
        rel_data = {
            "since": datetime.now().isoformat(),
            "guidanceType": "strategic",
            "notes": f"Founder định hướng hoạt động của {agent['name']}"
        }
        desc = f"Founder -> GUIDES -> Agent:{agent['name']}"
        if _create_relationship_request(endpoint, desc, rel_data):
            relationships_created_count += 1
    
    # --- Specific relationship for AGE ---
    # AGE là agent đặc biệt, có mối quan hệ cộng sinh với Founder
    age_agent = next((a for a in agents if a['agent_type'] == 'AGE'), None)
    if age_agent:
        # AGE MANAGED_BY Founder
        endpoint = f"/agents/{age_agent['agentId']}/managed-by/{founder['agentId']}"
        rel_data = {
            "since": datetime.now().isoformat(),
            "managementType": "strategic_direction",
            "notes": "AGE được quản lý và định hướng bởi Founder"
        }
        desc = f"AGE -> MANAGED_BY -> Founder"
        if _create_relationship_request(endpoint, desc, rel_data):
            relationships_created_count += 1
            
    return relationships_created_count

def verify_founder_in_neo4j(founder_id: str) -> bool:
    """Verify that the Founder exists in Neo4j with correct properties."""
    console.print("\n🔍 Verifying Founder in Neo4j...")
    try:
        # Get a Neo4j driver
        driver = get_driver()
        with driver.session() as session:
            result = session.run(
                """MATCH (f:Agent {agentId: $agentId}) 
                   RETURN f.name AS name, f.agent_type AS agentType, f.is_founder AS isFounder""",
                agentId=founder_id
            )
            record = result.single()
            if record and record["isFounder"] and record["agentType"] == "InternalAgent":
                console.print(f"✅ [green]Verified Founder in Neo4j:[/green] {record['name']}")
                return True
            else:
                console.print("❌ [bold red]Founder verification failed in Neo4j[/bold red]")
                return False
            
    except Exception as e:
        console.print(f"❌ [bold red]Error verifying Founder in Neo4j:[/bold red] {str(e)}")
        return False

def main():
    console.rule("[bold cyan]🚀 Seeding Founder (InternalAgent) Data 🚀[/bold cyan]")

    if not health_check():
        console.rule("[bold red]Seeding Aborted[/bold red]")
        return

    # --- Create Founder and test entities ---
    founder = create_founder()
    resources = create_test_resources()
    projects = create_test_projects()
    agents = create_test_agents()

    if not founder:
        console.print("❌ [bold red]Failed to create Founder. Aborting further seeding.[/bold red]")
        return

    # --- Create Founder Relationships ---
    relationship_count = create_founder_relationships(founder, resources, projects, agents)

    # --- Verify Founder in Neo4j ---
    neo4j_verified = verify_founder_in_neo4j(founder['agentId'])

    # --- Summary ---
    console.rule("[bold blue]Summary of Founder Seeding[/bold blue]")
    table = Table(title="Created Items")
    table.add_column("Item Type", justify="right", style="cyan", no_wrap=True)
    table.add_column("Count", justify="center", style="magenta")
    table.add_column("Status", justify="left", style="green")
    
    table.add_row("Founder", "1", "✅ Created" if founder else "❌ Failed")
    table.add_row("Resources", str(len(resources)), "✅ Created" if resources else "❌ Failed")
    table.add_row("Projects", str(len(projects)), "✅ Created" if projects else "❌ Failed")
    table.add_row("Agents", str(len(agents)), "✅ Created" if agents else "❌ Failed")
    table.add_row("Founder Relationships", str(relationship_count), "✅ Created" if relationship_count > 0 else "❌ Failed")
    table.add_row("Neo4j Verification", "1", "✅ Verified" if neo4j_verified else "❌ Failed")
    
    console.print(table)

    if founder and relationship_count > 0 and neo4j_verified:
        console.rule("[bold green]✅ Founder Seeding Completed Successfully ✅[/bold green]")
    else:
        console.rule("[bold red]⚠️ Founder Seeding Completed with Issues ⚠️[/bold red]")

    # --- Print UIDs for Event API testing ---
    if founder and founder.get('agentId'):
        console.print(f"\n[bold yellow]--- For Event API Testing ---[/bold yellow]")
        console.print(f"Founder (Actor) UID: [bold cyan]{founder['agentId']}[/bold cyan]")
        if projects and len(projects) > 0 and projects[0].get('projectId'):
            console.print(f"Test Project (Context) UID: [bold cyan]{projects[0]['projectId']}[/bold cyan]")
            console.print(f"Test Project (Context) Label: [bold cyan]Project[/bold cyan]")
        else:
            console.print("No test projects created or project UID not found.")
    else:
        console.print("\n[bold red]Could not retrieve Founder UID for Event API testing.[/bold red]")

if __name__ == "__main__":
    main()
