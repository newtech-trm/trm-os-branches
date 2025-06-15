#!/usr/bin/env python
# coding: utf-8

"""
Script kiểm thử trực tiếp với Neo4j để xác thực triển khai ontology V3.2.
Script này không phụ thuộc vào API server, chỉ kết nối trực tiếp với Neo4j.
"""

import sys
import os
import json
from typing import Dict, List, Any, Tuple
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Thêm project root vào Python path để cho phép import từ trm_api
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Tải cấu hình từ .env file (nếu có)
load_dotenv()

# --- Cấu hình ---
# Cấu hình Neo4j từ biến môi trường hoặc sử dụng giá trị mặc định
NEO4J_URI = os.environ.get('NEO4J_URI', 'neo4j+s://66abf65c.databases.neo4j.io')
NEO4J_USER = os.environ.get('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD', 'your_password_here')

console = Console()

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

# Danh sách các relationship cần xác thực theo ontology V3.2
ONTOLOGY_RELATIONSHIPS = [
    ("ASSIGNS_TASK", "User", "Task"),
    ("LEADS_TO_WIN", "Project", "WIN"),
    ("RESOLVES_TENSION", "Project", "Tension"),
    ("GENERATES_EVENT", "Task", "Event"),
    ("HAS_TASK", "Project", "Task"),
    ("HAS_SKILL", "User", "GraphSkill"),
    ("PARTICIPATES_IN", "User", "Team"),
    ("MANAGES_PROJECT", "User", "Project"),
    ("IS_PART_OF", "Task", "Project"),
    ("CONTRIBUTES_TO", "User", "Project"),
    ("RELATES_TO", "KnowledgeSnippet", "Task"),
    ("GENERATED_BY", "KnowledgeSnippet", "Agent"),
]

# Danh sách các entity labels cần xác thực theo ontology V3.2
ONTOLOGY_ENTITIES = [
    "User", 
    "Project", 
    "Task", 
    "Team", 
    "WIN", 
    "Tension", 
    "Event", 
    "GraphSkill",
    "KnowledgeSnippet",
    "Agent",
    "Action"
]

# --- Helper Functions ---

class Neo4jDriver:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def run_query(self, query, params=None):
        with self.driver.session() as session:
            result = session.run(query, params)
            return [record.data() for record in result]

def run_cypher_query(driver, query: str, params: Dict = None) -> List[Dict]:
    """Thực thi Cypher query và trả về kết quả."""
    try:
        return driver.run_query(query, params)
    except Exception as e:
        console.print(f"[bold red]Lỗi khi thực thi Cypher query: {e}[/bold red]")
        return []

def check_neo4j_connection(driver):
    """Kiểm tra kết nối với Neo4j."""
    console.print("Kiểm tra kết nối với Neo4j...", style="bold blue")
    
    try:
        result = driver.run_query("MATCH (n) RETURN count(n) as count LIMIT 1")
        count = result[0]["count"] if result else 0
        console.print(f"✅ [green]Kết nối Neo4j thành công! Có {count} node trong database.[/green]")
        return True
    except Exception as e:
        console.print(f"❌ [bold red]Không thể kết nối tới Neo4j: {e}[/bold red]")
        return False

def run_all_cypher_tests(driver):
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
                results = run_cypher_query(driver, query)
                
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

def validate_ontology_relationships(driver):
    """Xác thực các relationship quan trọng trong ontology."""
    console.rule("[bold blue]Xác thực Các Relationship Quan trọng[/bold blue]")
    
    table = Table(title="Xác thực Relationship Ontology")
    table.add_column("Relationship", style="cyan")
    table.add_column("Source Entity", style="blue")
    table.add_column("Target Entity", style="blue")
    table.add_column("Trạng thái", style="green")
    table.add_column("Số lượng", style="yellow")
    
    with Progress() as progress:
        task = progress.add_task("[green]Đang xác thực relationships...", total=len(ONTOLOGY_RELATIONSHIPS))
        
        for rel_type, source_type, target_type in ONTOLOGY_RELATIONSHIPS:
            query = f"""
            MATCH (s:{source_type})-[r:{rel_type}]->(t:{target_type})
            RETURN count(r) as count
            """
            
            try:
                results = run_cypher_query(driver, query)
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

def validate_ontology_entities(driver):
    """Xác thực các entity labels trong ontology."""
    console.rule("[bold blue]Xác thực Các Entity Labels[/bold blue]")
    
    table = Table(title="Xác thực Entity Labels Ontology")
    table.add_column("Entity Label", style="cyan")
    table.add_column("Trạng thái", style="green")
    table.add_column("Số lượng", style="yellow")
    
    with Progress() as progress:
        task = progress.add_task("[green]Đang xác thực entity labels...", total=len(ONTOLOGY_ENTITIES))
        
        for entity_label in ONTOLOGY_ENTITIES:
            query = f"""
            MATCH (n:{entity_label})
            RETURN count(n) as count
            """
            
            try:
                results = run_cypher_query(driver, query)
                count = results[0].get("count", 0) if results else 0
                
                if count > 0:
                    status = "✅ Tồn tại"
                else:
                    status = "⚠️ Không có data"
                
            except Exception as e:
                status = "❌ Lỗi"
                count = f"Error: {e}"
            
            table.add_row(entity_label, status, str(count))
            progress.update(task, advance=1)
    
    console.print(table)

def run_all_tests():
    """Chạy tất cả các kiểm thử."""
    console.print("Bắt đầu kiểm thử trực tiếp Neo4j cho ontology V3.2...", style="bold blue")
    
    # Kết nối với Neo4j
    driver = Neo4jDriver(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    # Kiểm tra kết nối
    if not check_neo4j_connection(driver):
        console.print("Không thể tiếp tục kiểm thử do lỗi kết nối với Neo4j. Vui lòng kiểm tra lại thông tin kết nối.", style="bold red")
        return
    
    try:
        # Chạy các kiểm thử
        run_all_cypher_tests(driver)
        validate_ontology_relationships(driver)
        validate_ontology_entities(driver)
        
        console.print("Hoàn thành kiểm thử trực tiếp Neo4j!", style="bold green")
    finally:
        # Đóng kết nối
        driver.close()

if __name__ == "__main__":
    run_all_tests()
