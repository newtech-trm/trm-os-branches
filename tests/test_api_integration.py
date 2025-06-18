#!/usr/bin/env python3
"""
Kiểm thử tích hợp cho các API endpoint của TRM-OS
Sử dụng kết nối Neo4j thật theo nguyên tắc ontology-first
"""

import pytest
import json
import uuid
from datetime import datetime
from fastapi.testclient import TestClient
from pprint import pprint

# Import các fixture từ conftest.py
# - test_client: TestClient để test API
# - seed_test_data: Fixture tạo dữ liệu test và cleanup


def generate_uuid():
    """Tạo UUID ngẫu nhiên"""
    return str(uuid.uuid4())


def print_response(response, label=None):
    """In ra response để debug"""
    if label:
        print(f"\n--- {label} ---")
    
    print(f"Status Code: {response.status_code}")
    try:
        pprint(response.json())
    except Exception:
        print(response.text)
    print()


def assert_status_code(response, expected_code=200):
    """Kiểm tra status code của response"""
    assert response.status_code == expected_code, f"Expected status {expected_code}, got {response.status_code}. Response: {response.text}"


def assert_response_has_field(response, field_name):
    """Kiểm tra response có chứa trường dữ liệu cụ thể"""
    try:
        data = response.json()
        assert field_name in data, f"Field '{field_name}' not found in response: {data}"
    except Exception as e:
        assert False, f"Failed to check field '{field_name}': {e}. Response: {response.text}"


class TestRecognitionAPI:
    """Test suite cho Recognition API endpoints"""

    @pytest.mark.integration
    def test_recognition_crud(self, test_client, seed_test_data):
        """Test các thao tác CRUD cho Recognition API"""
        # Lấy các ID đã seed từ fixture
        test_data = seed_test_data
        user_id = test_data["user1_id"]
        
        # 1. Tạo Recognition
        print("\n=== TEST TẠO RECOGNITION MỚI ===")
        recognition_data = {
            "title": "Test Recognition via API",
            "description": "Recognition được tạo bởi integration test", 
            "winId": test_data["win_id"],  # ID của WIN được ghi nhận
            "granterId": user_id,  # ID người tạo recognition
            "recipientIds": [test_data["user2_id"]],  # Mảng IDs người nhận
            "recognitionDate": datetime.now().isoformat(),  # Thêm ngày ghi nhận
            "recognitionType": "Gratitude"  # Đổi sang giá trị hợp lệ theo model
            # Bỏ các trường không có trong schema: impact_score, tags, is_test_data
        }
        
        # Gửi request tạo Recognition
        response = test_client.post(
            "/api/v1/recognitions/",
            json=recognition_data
        )
        print_response(response, "Create Recognition Response")
        assert_status_code(response, 201)
        
        # Lưu ID của Recognition để sử dụng tiếp
        recognition_id = response.json()["id"]
        assert recognition_id, "Recognition ID should not be empty"
        
        # 2. Lấy chi tiết Recognition
        print("\n=== TEST LẤY CHI TIẾT RECOGNITION ===")
        response = test_client.get(f"/api/v1/recognitions/{recognition_id}")
        print_response(response, "Get Recognition Detail")
        assert_status_code(response)
        
        # Kiểm tra thông tin chi tiết
        data = response.json()
        assert data["title"] == recognition_data["title"]
        assert data["sender_id"] == recognition_data["sender_id"]
        
        # 3. Cập nhật Recognition
        print("\n=== TEST CẬP NHẬT RECOGNITION ===")
        update_data = {
            "title": "Updated Recognition Title",
            "description": "Description đã được cập nhật",
            "impact_score": 5
        }
        
        response = test_client.patch(
            f"/api/v1/recognitions/{recognition_id}",
            json=update_data
        )
        print_response(response, "Update Recognition Response")
        assert_status_code(response)
        
        # Kiểm tra thông tin đã cập nhật
        assert response.json()["title"] == update_data["title"]
        assert response.json()["impact_score"] == update_data["impact_score"]
        
        # 4. Lấy danh sách Recognition
        print("\n=== TEST LẤY DANH SÁCH RECOGNITION ===")
        response = test_client.get("/api/v1/recognitions/")
        print_response(response, "List Recognitions Response")
        assert_status_code(response)
        
        # Kiểm tra cấu trúc response danh sách
        data = response.json()
        assert "items" in data, "Response should contain 'items' field"
        assert isinstance(data["items"], list), "'items' should be a list"
        
        # 5. Xóa Recognition
        print("\n=== TEST XÓA RECOGNITION ===")
        response = test_client.delete(f"/api/v1/recognitions/{recognition_id}")
        print_response(response, "Delete Recognition Response")
        assert_status_code(response, 204)
        
        # Kiểm tra Recognition đã xóa
        response = test_client.get(f"/api/v1/recognitions/{recognition_id}")
        assert response.status_code == 404, f"Recognition {recognition_id} should be deleted"


class TestRelationshipAPI:
    """Test suite cho Relationship API endpoints"""
    
    @pytest.mark.integration
    def test_relationship_crud(self, test_client, seed_test_data):
        """Test các thao tác CRUD cho Relationship API"""
        # Lấy các ID đã seed từ fixture
        test_data = seed_test_data
        user1_id = test_data["user1_id"]
        user2_id = test_data["user2_id"]
        
        # 1. Tạo Relationship
        print("\n=== TEST TẠO RELATIONSHIP MỚI ===")
        relationship_data = {
            "source_id": user1_id,
            "target_id": user2_id,
            "relationship_type": "COLLABORATES_WITH",
            "properties": {
                "since": datetime.now().isoformat(),
                "collaboration_level": "High",
                "is_test_data": True
            }
        }
        
        # Gửi request tạo Relationship qua query params vì API yêu cầu
        response = test_client.post(
            "/api/v1/relationships/",
            params={
                "source_id": relationship_data["source_id"],
                "source_type": "User",  # Phải dùng chí́nh xác enum từ API ("User" không phải "USER")
                "target_id": relationship_data["target_id"],
                "target_type": "User",  # Phải dùng chí́nh xác enum từ API ("User" không phải "USER")
                "relationship_type": "RELATES_TO"  # Sử dụng relationship_type hợp lệ theo enum
            }
        )
        print_response(response, "Create Relationship Response")
        assert_status_code(response, 201)
        
        # Lưu ID của Relationship để sử dụng tiếp
        relationship_id = response.json()["id"]
        assert relationship_id, "Relationship ID should not be empty"
        
        # 2. Lấy chi tiết Relationship
        print("\n=== TEST LẤY CHI TIẾT RELATIONSHIP ===")
        response = test_client.get(f"/api/v1/relationships/{relationship_id}")
        print_response(response, "Get Relationship Detail")
        assert_status_code(response)
        
        # Kiểm tra thông tin chi tiết
        data = response.json()
        assert data["source_id"] == relationship_data["source_id"]
        assert data["target_id"] == relationship_data["target_id"]
        assert data["relationship_type"] == relationship_data["relationship_type"]
        
        # 3. Cập nhật Relationship
        print("\n=== TEST CẬP NHẬT RELATIONSHIP ===")
        update_data = {
            "properties": {
                "collaboration_level": "Very High",
                "updated_at": datetime.now().isoformat()
            }
        }
        
        response = test_client.patch(
            f"/api/v1/relationships/{relationship_id}",
            json=update_data
        )
        print_response(response, "Update Relationship Response")
        assert_status_code(response)
        
        # Kiểm tra thông tin đã cập nhật
        assert response.json()["properties"]["collaboration_level"] == "Very High"
        
        # 4. Lấy danh sách Relationship
        print("\n=== TEST LẤY DANH SÁCH RELATIONSHIP ===")
        response = test_client.get("/api/v1/relationships/")
        print_response(response, "List Relationships Response")
        assert_status_code(response)
        
        # Kiểm tra cấu trúc response danh sách
        data = response.json()
        assert "items" in data, "Response should contain 'items' field"
        assert isinstance(data["items"], list), "'items' should be a list"
        
        # 5. Lọc Relationship theo loại
        print("\n=== TEST LỌC RELATIONSHIP THEO LOẠI ===")
        response = test_client.get(
            "/api/v1/relationships/",
            params={"relationship_type": "COLLABORATES_WITH"}
        )
        print_response(response, "Filter Relationships by Type")
        assert_status_code(response)
        
        # Kiểm tra kết quả lọc
        items = response.json()["items"]
        if items:  # Nếu có kết quả
            assert all(item["relationship_type"] == "COLLABORATES_WITH" for item in items)
        
        # 6. Xóa Relationship
        print("\n=== TEST XÓA RELATIONSHIP ===")
        response = test_client.delete(f"/api/v1/relationships/{relationship_id}")
        print_response(response, "Delete Relationship Response")
        assert_status_code(response, 204)
        
        # Kiểm tra Relationship đã xóa
        response = test_client.get(f"/api/v1/relationships/{relationship_id}")
        assert response.status_code == 404, f"Relationship {relationship_id} should be deleted"


class TestKnowledgeAPI:
    """Test suite cho Knowledge API endpoints"""
    
    @pytest.mark.integration
    def test_knowledge_crud(self, test_client, seed_test_data):
        """Test các thao tác CRUD cho Knowledge API"""
        test_data = seed_test_data
        
        # 1. Tạo Knowledge
        print("\n=== TEST TẠO KNOWLEDGE MỚI ===")
        knowledge_data = {
            "title": "Test Knowledge Item",
            "content": "Nội dung kiến thức test integration",
            "snippetType": "CONCEPT",  # Đổi knowledge_type -> snippetType theo yêu cầu API
            "tags": ["test", "api", "integration"],
            "created_by": test_data["user1_id"],
            "is_test_data": True
        }
        
        response = test_client.post(
            "/api/v1/knowledge-snippets/",
            json=knowledge_data
        )
        print_response(response, "Create Knowledge Response")
        assert_status_code(response, 201)
        
        # Lưu ID của Knowledge để sử dụng tiếp
        knowledge_id = response.json()["id"]
        assert knowledge_id, "Knowledge ID should not be empty"
        
        # 2. Lấy chi tiết Knowledge
        print("\n=== TEST LẤY CHI TIẾT KNOWLEDGE ===")
        response = test_client.get(f"/api/v1/knowledge-snippets/{knowledge_id}")
        print_response(response, "Get Knowledge Detail")
        assert_status_code(response)
        
        # 3. Cập nhật Knowledge
        print("\n=== TEST CẬP NHẬT KNOWLEDGE ===")
        update_data = {
            "title": "Updated Knowledge Title",
            "tags": ["test", "updated", "integration"]
        }
        
        response = test_client.patch(
            f"/api/v1/knowledge-snippets/{knowledge_id}",
            json=update_data
        )
        print_response(response, "Update Knowledge Response")
        assert_status_code(response)
        
        # Kiểm tra thông tin đã cập nhật
        assert response.json()["title"] == update_data["title"]
        assert set(response.json()["tags"]) == set(update_data["tags"])
        
        # 4. Lấy danh sách Knowledge
        print("\n=== TEST LẤY DANH SÁCH KNOWLEDGE ===")
        response = test_client.get("/api/v1/knowledge-snippets/")
        print_response(response, "List Knowledge Response")
        assert_status_code(response)
        
        # 5. Xóa Knowledge
        print("\n=== TEST XÓA KNOWLEDGE ===")
        response = test_client.delete(f"/api/v1/knowledge-snippets/{knowledge_id}")
        print_response(response, "Delete Knowledge Response")
        assert_status_code(response, 204)
        
        # Kiểm tra Knowledge đã xóa
        response = test_client.get(f"/api/v1/knowledge-snippets/{knowledge_id}")
        assert response.status_code == 404, f"Knowledge {knowledge_id} should be deleted"
