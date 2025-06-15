#!/usr/bin/env python
"""
Script Python kiểm tra API server và Neo4j Aura
"""
import os
import json
import requests
from neo4j import GraphDatabase
import uuid

# Thông tin kết nối API
API_BASE_URL = "http://127.0.0.1:8002"

# Thông tin kết nối Neo4j (từ .env)
NEO4J_URI = "66abf65c.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "VjZZx4wz6wttzQxSfu_j4_GQllwCjTP0Zmb6wSRXD40"

# Tạo mã project ngẫu nhiên để dễ tìm kiếm
test_id = str(uuid.uuid4())[:8]

def call_api(endpoint, method="GET", data=None):
    """Gọi API server"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    print(f"Gọi API: {method} {url}")
    if data:
        print(f"Dữ liệu gửi: {json.dumps(data, ensure_ascii=False)}")
    
    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=data)
    else:
        raise ValueError(f"Phương thức không hỗ trợ: {method}")
    
    print(f"Status code: {response.status_code}")
    try:
        return response.json()
    except:
        return response.text

def check_neo4j_data(query, params=None):
    """Truy vấn trực tiếp Neo4j"""
    uri = f"neo4j+s://{NEO4J_URI}"
    driver = GraphDatabase.driver(uri, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    print(f"Truy vấn Neo4j: {query}")
    if params:
        print(f"Params: {params}")
    
    with driver.session() as session:
        result = session.run(query, params)
        records = [record for record in result]
    
    driver.close()
    return records

def main():
    """Hàm chính kiểm tra API và Neo4j"""
    try:
        # 1. Tạo Project mới qua API
        print("===== 1. TẠO PROJECT QUA API =====")
        project_data = {
            "title": f"Test Project {test_id}",
            "description": f"Dự án kiểm tra Neo4j với ID {test_id}"
        }
        response = call_api("/api/v1/projects/", method="POST", data=project_data)
        print(f"Kết quả: {response}")
        
        # 2. Kiểm tra dữ liệu trực tiếp trong Neo4j
        print("\n===== 2. KIỂM TRA DỮ LIỆU TRONG NEO4J =====")
        query = "MATCH (p:Project) WHERE p.title CONTAINS $test_id RETURN p"
        records = check_neo4j_data(query, {"test_id": test_id})
        
        if records:
            print(f"Tìm thấy {len(records)} Project trong Neo4j:")
            for record in records:
                print(f"  - {record['p']}")
            print("\nXÁC NHẬN: Dữ liệu đã được lưu vào Neo4j Aura Cloud!")
        else:
            print("CẢNH BÁO: Không tìm thấy Project trong Neo4j!")
            print("Điều này có nghĩa API đã trả về thành công nhưng dữ liệu không được lưu vào Neo4j!")
        
        # 3. Kiểm tra các node trong Neo4j
        print("\n===== 3. THỐNG KÊ DỮ LIỆU TRONG NEO4J =====")
        query = "MATCH (n) RETURN labels(n) as Type, count(n) as Count"
        records = check_neo4j_data(query)
        
        if records:
            for record in records:
                print(f"  - {record['Type']}: {record['Count']} nodes")
        else:
            print("CẢNH BÁO: Không tìm thấy node nào trong Neo4j!")
        
    except Exception as e:
        print(f"Lỗi: {str(e)}")

if __name__ == "__main__":
    main()
