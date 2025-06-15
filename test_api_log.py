#!/usr/bin/env python
"""
Script Python kiểm tra API server và Neo4j Aura kèm ghi log
"""
import os
import json
import requests
from neo4j import GraphDatabase
import uuid
import logging

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("neo4j_api_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
    
    logger.info(f"Gọi API: {method} {url}")
    if data:
        logger.info(f"Dữ liệu gửi: {json.dumps(data, ensure_ascii=False)}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Phương thức không hỗ trợ: {method}")
        
        logger.info(f"Status code: {response.status_code}")
        try:
            result = response.json()
            logger.info(f"Response: {json.dumps(result, ensure_ascii=False)}")
            return result
        except:
            logger.info(f"Response text: {response.text}")
            return response.text
    except Exception as e:
        logger.error(f"Lỗi khi gọi API: {e}")
        raise

def check_neo4j_data(query, params=None):
    """Truy vấn trực tiếp Neo4j"""
    uri = f"neo4j+s://{NEO4J_URI}"
    
    logger.info(f"Kết nối Neo4j: {uri}")
    logger.info(f"Truy vấn: {query}")
    if params:
        logger.info(f"Params: {params}")
    
    try:
        driver = GraphDatabase.driver(uri, auth=(NEO4J_USER, NEO4J_PASSWORD))
        logger.info("Kết nối Neo4j thành công")
        
        with driver.session() as session:
            result = session.run(query, params)
            records = [record for record in result]
        
        driver.close()
        logger.info(f"Kết quả truy vấn: {len(records)} records")
        return records
    except Exception as e:
        logger.error(f"Lỗi khi truy vấn Neo4j: {e}")
        raise

def main():
    """Hàm chính kiểm tra API và Neo4j"""
    logger.info("===== BẮT ĐẦU KIỂM TRA API VÀ NEO4J =====")
    logger.info(f"Test ID: {test_id}")
    
    try:
        # 1. Tạo Project mới qua API
        logger.info("\n===== 1. TẠO PROJECT QUA API =====")
        project_data = {
            "title": f"Test Project {test_id}",
            "description": f"Dự án kiểm tra Neo4j với ID {test_id}"
        }
        response = call_api("/api/v1/projects/", method="POST", data=project_data)
        
        # 2. Kiểm tra xem API có hoạt động không
        logger.info("\n===== 2. KIỂM TRA API CÓ HOẠT ĐỘNG KHÔNG =====")
        users_response = call_api("/api/v1/users/", method="GET")
        
        # 3. Kiểm tra dữ liệu trực tiếp trong Neo4j
        logger.info("\n===== 3. KIỂM TRA DỮ LIỆU TRONG NEO4J =====")
        query = "MATCH (p:Project) WHERE p.title CONTAINS $test_id RETURN p"
        records = check_neo4j_data(query, {"test_id": test_id})
        
        if records:
            logger.info(f"Tìm thấy {len(records)} Project trong Neo4j:")
            for record in records:
                logger.info(f"  - {record['p']}")
            logger.info("\nXÁC NHẬN: Dữ liệu đã được lưu vào Neo4j Aura Cloud!")
        else:
            logger.warning("CẢNH BÁO: Không tìm thấy Project trong Neo4j!")
            logger.warning("Điều này có nghĩa API đã trả về thành công nhưng dữ liệu không được lưu vào Neo4j!")
        
        # 4. Kiểm tra các node trong Neo4j
        logger.info("\n===== 4. THỐNG KÊ DỮ LIỆU TRONG NEO4J =====")
        query = "MATCH (n) RETURN labels(n) as Type, count(n) as Count"
        records = check_neo4j_data(query)
        
        if records:
            for record in records:
                logger.info(f"  - {record['Type']}: {record['Count']} nodes")
        else:
            logger.warning("CẢNH BÁO: Không tìm thấy node nào trong Neo4j!")
        
    except Exception as e:
        logger.error(f"Lỗi khi kiểm tra: {str(e)}")
    
    logger.info("===== KẾT THÚC KIỂM TRA =====")

if __name__ == "__main__":
    main()
