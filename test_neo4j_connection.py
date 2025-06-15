#!/usr/bin/env python
"""
Script kiểm tra kết nối đến Neo4j Aura và hiển thị dữ liệu thực tế
"""
import sys
sys.path.append('.')

try:
    from trm_api.db.graph_connection import get_neo4j_driver
    print("Module graph_connection được import thành công")
except ImportError as e:
    print(f"Lỗi import module: {e}")
    sys.exit(1)

try:
    # Kết nối đến Neo4j Aura
    driver = get_neo4j_driver()
    print("Kết nối đến Neo4j thành công")
    
    # Kiểm tra thống kê dữ liệu
    with driver.session() as session:
        # Thống kê loại node
        result = session.run('MATCH (n) RETURN labels(n) as Type, count(n) as Count')
        print("\n== Thống kê dữ liệu Neo4j Aura ==")
        for record in result:
            print(f"{record['Type']}: {record['Count']} nodes")
        
        # Lấy danh sách Project
        print("\n== 5 Project mới nhất ==")
        result = session.run('MATCH (p:Project) RETURN p.title as Title, p.description as Description LIMIT 5')
        project_count = 0
        for record in result:
            project_count += 1
            print(f"Project: {record['Title']} - {record['Description']}")
        
        if project_count == 0:
            print("Không tìm thấy Project nào trong database!")
        
        # Lấy danh sách Task
        print("\n== 5 Task mới nhất ==")
        result = session.run('MATCH (t:Task) RETURN t.name as Name, t.description as Description LIMIT 5')
        task_count = 0
        for record in result:
            task_count += 1
            print(f"Task: {record['Name']} - {record['Description']}")
        
        if task_count == 0:
            print("Không tìm thấy Task nào trong database!")
        
        # Kiểm tra Relationship
        print("\n== Relationships ==")
        result = session.run('MATCH ()-[r]->() RETURN type(r) as Type, count(r) as Count')
        rel_count = 0
        for record in result:
            rel_count += 1
            print(f"Relationship: {record['Type']} - {record['Count']} relationships")
        
        if rel_count == 0:
            print("Không tìm thấy Relationship nào trong database!")
    
    driver.close()
    print("\nĐã đóng kết nối Neo4j")

except Exception as e:
    print(f"Lỗi khi kết nối hoặc truy vấn Neo4j: {e}")
    sys.exit(1)
