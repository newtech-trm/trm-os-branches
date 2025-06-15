#!/usr/bin/env python
"""
Kết nối trực tiếp đến Neo4j Aura và kiểm tra dữ liệu
"""
from neo4j import GraphDatabase
import os
import dotenv
import sys

# Tải biến môi trường từ .env
dotenv.load_dotenv()

# Lấy thông tin kết nối Neo4j
neo4j_uri = os.getenv("NEO4J_URI", "")
neo4j_user = os.getenv("NEO4J_USER", "")
neo4j_password = os.getenv("NEO4J_PASSWORD", "")

# Kiểm tra thông tin kết nối
print(f"URI: {neo4j_uri}")
print(f"User: {neo4j_user}")
print(f"Password: {'*' * len(neo4j_password) if neo4j_password else 'Không có'}")

if not all([neo4j_uri, neo4j_user, neo4j_password]):
    print("Thiếu thông tin kết nối Neo4j trong .env file")
    sys.exit(1)

# Cấu trúc URI đầy đủ cho Neo4j Aura
full_uri = f"neo4j+s://{neo4j_uri}" if not neo4j_uri.startswith("neo4j+s://") else neo4j_uri

try:
    # Kết nối đến Neo4j Aura
    driver = GraphDatabase.driver(full_uri, auth=(neo4j_user, neo4j_password))
    print(f"Kết nối đến Neo4j Aura thành công: {full_uri}")
    
    # Kiểm tra kết nối
    with driver.session() as session:
        # Thống kê loại node
        result = session.run('MATCH (n) RETURN labels(n) as Type, count(n) as Count')
        print("\n== THỐNG KÊ DỮ LIỆU NEO4J AURA ==")
        record_count = 0
        for record in result:
            record_count += 1
            print(f"{record['Type']}: {record['Count']} nodes")
        
        if record_count == 0:
            print("CẢNH BÁO: Không có node nào trong database!")
        
        # Lấy danh sách Project
        print("\n== 5 PROJECT MỚI NHẤT ==")
        result = session.run('MATCH (p:Project) RETURN p.title as Title, p.description as Description LIMIT 5')
        project_count = 0
        for record in result:
            project_count += 1
            print(f"Project: {record['Title']} - {record['Description']}")
        
        if project_count == 0:
            print("CẢNH BÁO: Không tìm thấy Project nào trong database!")
        
        # Lấy danh sách Task
        print("\n== 5 TASK MỚI NHẤT ==")
        result = session.run('MATCH (t:Task) RETURN t.name as Name, t.description as Description LIMIT 5')
        task_count = 0
        for record in result:
            task_count += 1
            print(f"Task: {record['Name']} - {record['Description']}")
        
        if task_count == 0:
            print("CẢNH BÁO: Không tìm thấy Task nào trong database!")
        
        # Kiểm tra Relationship
        print("\n== MỐI QUAN HỆ (RELATIONSHIPS) ==")
        result = session.run('MATCH ()-[r]->() RETURN type(r) as Type, count(r) as Count')
        rel_count = 0
        for record in result:
            rel_count += 1
            print(f"Relationship: {record['Type']} - {record['Count']} relationships")
        
        if rel_count == 0:
            print("CẢNH BÁO: Không tìm thấy Relationship nào trong database!")
    
    driver.close()
    print("\nĐã đóng kết nối Neo4j")

except Exception as e:
    print(f"LỖI khi kết nối hoặc truy vấn Neo4j Aura: {str(e)}")
    sys.exit(1)
