#!/usr/bin/env python
# coding: utf-8

"""
Script kiểm thử toàn diện triển khai ontology V3.2 trong TRM-OS.

Kiểm thử:
1. Validation thông qua API (đảm bảo các endpoint hoạt động đúng)
2. Truy vấn Cypher mẫu (đảm bảo tính nhất quán của dữ liệu)
3. Xác nhận các relationship quan trọng trong ontology

Prerequisites:
- API server phải đang chạy trên cổng 8000
- Neo4j đã được bơm dữ liệu thông qua script seed_data.py
"""

import json
import sys
import os
import time
import requests
from typing import Dict, List, Any, Tuple
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

# Thêm project root vào Python path để cho phép import từ trm_api
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from trm_api.db.session import get_driver

# --- Cấu hình ---
BASE_URL = "http://127.0.0.1:8000/api/v1"
console = Console()

# Các endpoint API cần kiểm thử
API_ENDPOINTS = [
    # Core entity endpoints
    ("/users/", "GET", "Users API"),
    ("/projects/", "GET", "Projects API"),
    ("/tasks/", "GET", "Tasks API"),
    ("/teams/", "GET", "Teams API"),
    ("/wins/", "GET", "WINs API"),
    ("/tensions/", "GET", "Tensions API"),
    ("/events/", "GET", "Events API"),
    ("/knowledge-snippets/", "GET", "Knowledge Snippets API"),
    ("/skills/", "GET", "Skills API"),
    
    # Relationship endpoints
    ("/users/{id}/assigns-task", "GET", "AssignsTask Relationship API"),
    ("/projects/{id}/leads-to-win", "GET", "LeadsToWin Relationship API"),
    ("/projects/{id}/resolves-tension", "GET", "ResolvesTension Relationship API"),
    ("/users/{id}/has-skill", "GET", "HasSkill Relationship API"),
    ("/tasks/{id}/generates-event", "GET", "GeneratesEvent Relationship API"),
]

# Các Cypher query mẫu để kiểm thử
CYPHER_QUERIES = [
    (
        "Lấy tất cả User",
        """
        MATCH (u:User)
        RETURN u.username, u.email, u.full_name
        LIMIT 10
        """
    ),
    (
        "Lấy tất cả Project",
        """
        MATCH (p:Project)
        RETURN p.title, p.description, p.status
        LIMIT 10
        """
    ),
    (
        "Lấy tất cả Task",
        """
        MATCH (t:Task)
        RETURN t.name, t.description, t.status, t.effort
        LIMIT 10
        """
    ),
    (
        "Lấy tất cả WIN",
        """
        MATCH (w:WIN)
        RETURN w.summary, w.winType
        LIMIT 10
        """
    ),
    (
        "Lấy quan hệ User AssignsTask Task",
        """
        MATCH (u:User)-[r:ASSIGNS_TASK]->(t:Task)
        RETURN u.username, t.name, r.assignedDate, r.relationshipId
        LIMIT 10
        """
    ),
    (
        "Lấy quan hệ Project LeadsToWin WIN",
        """
        MATCH (p:Project)-[r:LEADS_TO_WIN]->(w:WIN)
        RETURN p.title, w.summary, r.relationshipId, r.createdAt
        LIMIT 10
        """
    ),
    (
        "Lấy quan hệ Project RESOLVES_TENSION Tension",
        """
        MATCH (p:Project)-[r:RESOLVES_TENSION]->(t:Tension)
        RETURN p.title, t.title, r.relationshipId, r.createdAt
        LIMIT 10
        """
    ),
    (
        "Lấy quan hệ Task GENERATES_EVENT Event",
        """
        MATCH (t:Task)-[r:GENERATES_EVENT]->(e:Event)
        RETURN t.name, e.title, r.relationshipId, r.createdAt
        LIMIT 10
        """
    ),
]

# --- Helper Functions ---

def run_cypher_query(query: str, params: Dict = None) -> List[Dict]:
    """Thực thi Cypher query và trả về kết quả."""
    driver = get_driver()
    with driver.session() as session:
        result = session.run(query, params)
        return [record.data() for record in result]

def test_api_endpoint(endpoint: str, method: str = "GET", description: str = "") -> Tuple[bool, Dict]:
    """Kiểm thử API endpoint và trả về kết quả."""
    try:
        # Xử lý placeholder {id} trong endpoint
        if "{id}" in endpoint:
            # Nếu endpoint chứa {id}, lấy ID từ endpoint gốc
            base_endpoint = endpoint.split("/{id}")[0]
            response = requests.get(f"{BASE_URL}{base_endpoint}")
            response.raise_for_status()
            
            results = response.json()
            if not results or not isinstance(results, list) or len(results) == 0:
                return False, {"error": f"Không tìm thấy dữ liệu cho endpoint {base_endpoint}"}
            
            # Lấy ID của item đầu tiên
            item_id = None
            if len(results) > 0:
                item = results[0]
                for key in ['id', 'userId', 'projectId', 'taskId', 'teamId', 'winId', 'tensionId']:
                    if key in item:
                        item_id = item[key]
                        break
            
            if not item_id:
                return False, {"error": f"Không tìm thấy ID trong kết quả từ {base_endpoint}"}
            
            # Thay thế {id} bằng ID thực tế
            endpoint = endpoint.replace("{id}", item_id)
        
        # Thực hiện request API
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}")
        else:
            return False, {"error": f"Phương thức không được hỗ trợ: {method}"}
            
        response.raise_for_status()
        return True, response.json()
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        if hasattr(e, "response") and e.response is not None:
            try:
                error_details = e.response.json()
                error_message = f"{error_message}: {json.dumps(error_details)}"
            except:
                error_message = f"{error_message}: {e.response.text}"
        
        return False, {"error": error_message}

def run_all_api_tests():
    """Chạy tất cả các kiểm thử API."""
    console.rule("[bold blue]Kiểm thử API Endpoints[/bold blue]")
    
    table = Table(title="Kết quả Kiểm thử API")
    table.add_column("Endpoint", style="cyan")
    table.add_column("Mô tả", style="blue")
    table.add_column("Trạng thái", style="green")
    table.add_column("Chi tiết", style="yellow")
    
    with Progress() as progress:
        task = progress.add_task("[green]Đang kiểm thử API...", total=len(API_ENDPOINTS))
        
        for endpoint, method, description in API_ENDPOINTS:
            success, result = test_api_endpoint(endpoint, method, description)
            
            if success:
                status = "✅ OK"
                details = "Thành công"
            else:
                status = "❌ Lỗi"
                details = result.get("error", "Không rõ lỗi")
            
            table.add_row(endpoint, description, status, details)
            progress.update(task, advance=1)
    
    console.print(table)

def run_all_cypher_tests():
    """Chạy tất cả các kiểm thử Cypher."""
    console.rule("[bold blue]Kiểm thử Cypher Queries[/bold blue]")
    
    table = Table(title="Kết quả Kiểm thử Cypher")
    table.add_column("Mô tả", style="cyan")
    table.add_column("Trạng thái", style="green")
    table.add_column("Kết quả", style="yellow")
    
    with Progress() as progress:
        task = progress.add_task("[green]Đang thực thi Cypher queries...", total=len(CYPHER_QUERIES))
        
        for description, query in CYPHER_QUERIES:
            try:
                results = run_cypher_query(query)
                
                if results and len(results) > 0:
                    status = "✅ OK"
                    result_text = f"{len(results)} bản ghi"
                else:
                    status = "⚠️ Không có dữ liệu"
                    result_text = "Truy vấn thành công nhưng không có kết quả"
            except Exception as e:
                status = "❌ Lỗi"
                result_text = str(e)
            
            table.add_row(description, status, result_text)
            progress.update(task, advance=1)
    
    console.print(table)

def validate_ontology_relationships():
    """Xác thực các relationship quan trọng trong ontology."""
    console.rule("[bold blue]Xác thực Các Relationship Quan trọng[/bold blue]")
    
    # Các relationship ontology cần kiểm thử
    relationships = [
        ("ASSIGNS_TASK", "User", "Task"),
        ("LEADS_TO_WIN", "Project", "WIN"),
        ("RESOLVES_TENSION", "Project", "Tension"),
        ("GENERATES_EVENT", "Task", "Event"),
        ("HAS_TASK", "Project", "Task"),
        ("HAS_SKILL", "User", "GraphSkill"),
        ("PARTICIPATES_IN", "User", "Team"),
        ("MANAGES_PROJECT", "User", "Project")
    ]
    
    table = Table(title="Xác thực Relationship Ontology")
    table.add_column("Relationship", style="cyan")
    table.add_column("Source Entity", style="blue")
    table.add_column("Target Entity", style="blue")
    table.add_column("Trạng thái", style="green")
    table.add_column("Số lượng", style="yellow")
    
    with Progress() as progress:
        task = progress.add_task("[green]Đang xác thực relationships...", total=len(relationships))
        
        for rel_type, source_type, target_type in relationships:
            query = f"""
            MATCH (s:{source_type})-[r:{rel_type}]->(t:{target_type})
            RETURN count(r) as count
            """
            
            try:
                results = run_cypher_query(query)
                count = results[0].get("count", 0) if results else 0
                
                if count > 0:
                    status = "✅ Tồn tại"
                else:
                    status = "⚠️ Không có data"
                
            except Exception as e:
                status = "❌ Lỗi"
                count = f"Error: {e}"
            
            table.add_row(rel_type, source_type, target_type, status, str(count))
            progress.update(task, advance=1)
    
    console.print(table)

def check_api_health():
    """Kiểm tra kết nối với API server."""
    console.print("Kiểm tra kết nối với API server...", style="bold blue")
    
    try:
        response = requests.get(f"{BASE_URL}/users/")
        response.raise_for_status()
        console.print("✅ [green]Kết nối API thành công![/green]")
        return True
    except requests.exceptions.RequestException as e:
        console.print(f"❌ [bold red]Không thể kết nối tới API server: {e}[/bold red]")
        console.print("Hãy đảm bảo server API đang chạy trên cổng 8000", style="yellow")
        return False

def check_neo4j_connection():
    """Kiểm tra kết nối với Neo4j."""
    console.print("Kiểm tra kết nối với Neo4j...", style="bold blue")
    
    try:
        driver = get_driver()
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as count")
            count = result.single()["count"]
            console.print(f"✅ [green]Kết nối Neo4j thành công! Có {count} node trong database.[/green]")
        return True
    except Exception as e:
        console.print(f"❌ [bold red]Không thể kết nối tới Neo4j: {e}[/bold red]")
        return False

def run_all_tests():
    """Chạy tất cả các kiểm thử."""
    console.print("Bắt đầu kiểm thử toàn diện triển khai ontology V3.2...", style="bold blue")
    
    # Kiểm tra kết nối
    if not check_api_health() or not check_neo4j_connection():
        console.print("Không thể tiếp tục kiểm thử do lỗi kết nối. Vui lòng khởi động API server và đảm bảo Neo4j đang chạy.", style="bold red")
        return
    
    # Chạy các kiểm thử
    run_all_api_tests()
    run_all_cypher_tests()
    validate_ontology_relationships()
    
    console.print("Hoàn thành kiểm thử toàn diện!", style="bold green")

if __name__ == "__main__":
    run_all_tests()
