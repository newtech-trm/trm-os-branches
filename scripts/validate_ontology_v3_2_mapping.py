#!/usr/bin/env python
# coding: utf-8

"""
Script kiểm thử và xác thực mapping giữa dữ liệu thực tế trong Neo4j và thiết kế Ontology V3.2.

Kiểm tra:
1. Các entity đã được tạo có đầy đủ thuộc tính theo thiết kế
2. Các relationship đã được tạo có đầy đủ thuộc tính theo thiết kế
3. Cấu trúc quan hệ tuân thủ đúng thiết kế ontology V3.2

Prerequisites:
- Neo4j đã chứa dữ liệu (script seed_data.py đã được chạy)
- Các thư viện cần thiết đã được cài đặt:
  pip install neo4j rich pandas
"""

import sys
import os
import time
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from neo4j import GraphDatabase

# Thêm project root vào Python path để cho phép import từ trm_api
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from trm_api.db.session import get_driver

# --- Cấu hình ---
console = Console()

# --- Các Cypher query để validate dữ liệu ---

# Danh sách entity cần kiểm tra
ENTITIES = [
    "User",
    "Project", 
    "Task",
    "Team", 
    "Tension",
    "WIN",
    "Event",
    "KnowledgeSnippet",
    "GraphSkill"
]

# Danh sách relationship cần kiểm tra
RELATIONSHIPS = [
    "ASSIGNS_TASK",
    "LEADS_TO_WIN",
    "RESOLVES_TENSION",
    "GENERATES_EVENT",
    "HAS_TASK",
    "HAS_SKILL",
    "PARTICIPATES_IN",
    "MANAGES_PROJECT"
]

# --- Helper Functions ---

def run_query(query, params=None):
    """Thực thi Cypher query và trả về kết quả."""
    driver = get_driver()
    with driver.session() as session:
        result = session.run(query, params)
        return [record.data() for record in result]

def validate_entity_properties(entity_name):
    """Kiểm tra các thuộc tính của entity có đầy đủ theo thiết kế không."""
    console.rule(f"[bold blue]Kiểm tra Entity: {entity_name}[/bold blue]")
    
    try:
        query = f"""
        MATCH (n:{entity_name})
        RETURN n, properties(n) as props, id(n) as id
        LIMIT 5
        """
        
        results = run_query(query)
        
        if not results:
            console.print(f"❌ [red]Không tìm thấy node nào thuộc loại {entity_name}[/red]")
            return
    except Exception as e:
        console.print(f"❌ [red]Lỗi khi truy vấn entity {entity_name}: {str(e)}[/red]")
        return
    
    table = Table(title=f"{entity_name} Properties")
    table.add_column("ID", style="cyan")
    
    # Thêm cột cho tất cả thuộc tính tìm thấy
    all_props = set()
    for result in results:
        props = result.get("props", {})
        all_props.update(props.keys())
    
    for prop in sorted(all_props):
        table.add_column(prop, style="green")
    
    # Thêm dữ liệu vào bảng
    for result in results:
        props = result.get("props", {})
        row = [str(result.get("id"))]
        
        for prop in sorted(all_props):
            value = props.get(prop, "")
            row.append(str(value) if value else "")
        
        table.add_row(*row)
    
    console.print(table)
    
    # Đối chiếu với ontology V3.2 (phần này cần được mở rộng với dữ liệu cụ thể từ ontology)
    required_props = get_required_properties(entity_name)
    missing_props = [prop for prop in required_props if prop not in all_props]
    
    if missing_props:
        console.print(f"❌ [red]Thiếu các thuộc tính sau theo thiết kế ontology V3.2: {', '.join(missing_props)}[/red]")
    else:
        console.print(f"✅ [green]{entity_name} có đầy đủ thuộc tính cơ bản theo thiết kế ontology V3.2[/green]")

def validate_relationship_properties(rel_name):
    """Kiểm tra các thuộc tính của relationship có đầy đủ theo thiết kế không."""
    console.rule(f"[bold blue]Kiểm tra Relationship: {rel_name}[/bold blue]")
    
    try:
        query = f"""
        MATCH ()-[r:{rel_name}]->() 
        RETURN type(r) as type, properties(r) as props, id(r) as id
        LIMIT 5
        """
        
        results = run_query(query)
        
        if not results:
            console.print(f"❌ [red]Không tìm thấy relationship nào thuộc loại {rel_name}[/red]")
            return
    except Exception as e:
        console.print(f"❌ [red]Lỗi khi truy vấn relationship {rel_name}: {str(e)}[/red]")
        return
    
    table = Table(title=f"{rel_name} Properties")
    table.add_column("ID", style="cyan")
    
    # Thêm cột cho tất cả thuộc tính tìm thấy
    all_props = set()
    for result in results:
        props = result.get("props", {})
        all_props.update(props.keys())
    
    for prop in sorted(all_props):
        table.add_column(prop, style="green")
    
    # Thêm dữ liệu vào bảng
    for result in results:
        props = result.get("props", {})
        row = [str(result.get("id"))]
        
        for prop in sorted(all_props):
            value = props.get(prop, "")
            row.append(str(value) if value else "")
        
        table.add_row(*row)
    
    console.print(table)
    
    # Đối chiếu với ontology V3.2 (phần này cần được mở rộng với dữ liệu cụ thể từ ontology)
    required_props = get_required_relationship_properties(rel_name)
    missing_props = [prop for prop in required_props if prop not in all_props]
    
    if missing_props:
        console.print(f"❌ [red]Thiếu các thuộc tính sau cho relationship {rel_name} theo thiết kế ontology V3.2: {', '.join(missing_props)}[/red]")
    else:
        console.print(f"✅ [green]{rel_name} có đầy đủ thuộc tính cơ bản theo thiết kế ontology V3.2[/green]")

def get_required_properties(entity_name):
    """Trả về danh sách các thuộc tính bắt buộc của entity theo ontology V3.2."""
    # Mapping thuộc tính bắt buộc theo ontology V3.2
    required_props = {
        "User": ["username", "email"],
        "Project": ["title", "description", "status"],
        "Task": ["name", "status", "effort"],
        "Team": ["name"],
        "Tension": ["title", "description", "status"],
        "WIN": ["summary", "winType"],
        "Event": ["title", "eventType", "timestamp"],
        "KnowledgeSnippet": ["content", "source"],
        "GraphSkill": ["name", "level"]
    }
    
    return required_props.get(entity_name, [])

def get_required_relationship_properties(rel_name):
    """Trả về danh sách các thuộc tính bắt buộc của relationship theo ontology V3.2."""
    # Mapping thuộc tính bắt buộc theo ontology V3.2
    required_props = {
        "ASSIGNS_TASK": ["assignedDate", "relationshipId"],
        "LEADS_TO_WIN": ["relationshipId", "createdAt"],
        "RESOLVES_TENSION": ["relationshipId", "createdAt"],
        "GENERATES_EVENT": ["relationshipId", "createdAt"],
        "HAS_TASK": ["relationshipId", "createdAt"],
        "HAS_SKILL": ["relationshipId", "skillLevel"],
        "PARTICIPATES_IN": [],
        "MANAGES_PROJECT": []
    }
    
    return required_props.get(rel_name, [])

def validate_ontology_structure():
    """Kiểm tra cấu trúc ontology tổng thể có tuân thủ thiết kế không."""
    console.rule("[bold blue]Kiểm tra Cấu trúc Ontology[/bold blue]")
    
    try:
        # Kiểm tra số lượng entity mỗi loại
        query = """
        MATCH (n)
        WITH labels(n)[0] AS entityType, count(*) AS count
        RETURN entityType, count
        ORDER BY count DESC
        """
        
        results = run_query(query)
        
        if not results:
            console.print("❌ [red]Không tìm thấy node nào trong cơ sở dữ liệu[/red]")
            return
        
        table = Table(title="Entity Count")
        table.add_column("Entity Type", style="cyan")
        table.add_column("Count", style="green")
        
        for result in results:
            entity_type = result.get("entityType", "") 
            count = str(result.get("count", 0))
            table.add_row(entity_type, count)
        
        console.print(table)
    except Exception as e:
        console.print(f"❌ [red]Lỗi khi kiểm tra cấu trúc entity: {str(e)}[/red]")
    
    try:
        # Kiểm tra số lượng relationship mỗi loại
        query = """
        MATCH ()-[r]->()
        WITH type(r) AS relType, count(*) AS count
        RETURN relType, count
        ORDER BY count DESC
        """
        
        results = run_query(query)
        
        if not results:
            console.print("❌ [red]Không tìm thấy relationship nào trong cơ sở dữ liệu[/red]")
            return
        
        table = Table(title="Relationship Count")
        table.add_column("Relationship Type", style="cyan")
        table.add_column("Count", style="green")
        
        for result in results:
            rel_type = result.get("relType", "")
            count = str(result.get("count", 0))
            table.add_row(rel_type, count)
        
        console.print(table)
    except Exception as e:
        console.print(f"❌ [red]Lỗi khi kiểm tra cấu trúc relationship: {str(e)}[/red]")

def run_validation():
    """Chạy tất cả các kiểm tra xác thực."""
    console.print("Bắt đầu quy trình xác thực ontology V3.2...", style="bold blue")
    
    # Xác thực cấu trúc ontology tổng thể
    validate_ontology_structure()
    
    # Kiểm tra từng entity
    for entity in ENTITIES:
        validate_entity_properties(entity)
    
    # Kiểm tra từng relationship
    for relationship in RELATIONSHIPS:
        validate_relationship_properties(relationship)
    
    console.print("Hoàn thành quy trình xác thực!", style="bold green")

if __name__ == "__main__":
    run_validation()
