#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script để seed và kiểm thử thực tế các thuộc tính mở rộng và relationship mới
của Project theo Ontology V3.2.
"""

import os
import sys
import json
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Any, Optional
import uuid
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API URL
BASE_URL = "http://127.0.0.1:8000"  # Địa chỉ API server

# Headers cho API request
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def check_api_health() -> bool:
    """Kiểm tra API server có đang chạy không."""
    try:
        response = requests.get(f"{BASE_URL}/health", headers=HEADERS)
        if response.status_code == 200:
            logger.info("API server đang hoạt động bình thường.")
            return True
        else:
            logger.error(f"API server có vấn đề: {response.status_code} - {response.text}")
            return False
    except requests.RequestException as e:
        logger.error(f"Không thể kết nối tới API server: {e}")
        return False

def get_all_projects() -> List[Dict[str, Any]]:
    """Lấy danh sách tất cả Project hiện có."""
    try:
        response = requests.get(f"{BASE_URL}/api/projects", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "items" in data:  # Kiểm tra nếu response là paginated
                return data["items"]
            return data
        else:
            logger.error(f"Không thể lấy danh sách Project: {response.status_code} - {response.text}")
            return []
    except requests.RequestException as e:
        logger.error(f"Lỗi kết nối khi lấy danh sách Project: {e}")
        return []

def get_all_users() -> List[Dict[str, Any]]:
    """Lấy danh sách tất cả User hiện có."""
    try:
        response = requests.get(f"{BASE_URL}/api/users", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "items" in data:  # Kiểm tra nếu response là paginated
                return data["items"]
            return data
        else:
            logger.error(f"Không thể lấy danh sách User: {response.status_code} - {response.text}")
            return []
    except requests.RequestException as e:
        logger.error(f"Lỗi kết nối khi lấy danh sách User: {e}")
        return []

def get_all_resources() -> List[Dict[str, Any]]:
    """Lấy danh sách tất cả Resource hiện có."""
    try:
        response = requests.get(f"{BASE_URL}/api/resources", headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "items" in data:  # Kiểm tra nếu response là paginated
                return data["items"]
            return data
        else:
            logger.error(f"Không thể lấy danh sách Resource: {response.status_code} - {response.text}")
            return []
    except requests.RequestException as e:
        logger.error(f"Lỗi kết nối khi lấy danh sách Resource: {e}")
        return []

def create_strategic_project() -> Optional[Dict[str, Any]]:
    """Tạo một Strategic Project với các thuộc tính mở rộng theo Ontology V3.2."""
    try:
        start_date = datetime.now().isoformat()
        target_end_date = (datetime.now() + timedelta(days=90)).isoformat()
        
        project_data = {
            "title": f"Dự án Chiến lược {uuid.uuid4().hex[:8]}",
            "description": "Một dự án chiến lược quan trọng theo Ontology V3.2 với nhiều thuộc tính mở rộng",
            "status": "active",
            "goal": "Đạt được sự phát triển bền vững và tạo giá trị cao cho hệ thống",
            "scope": "Toàn bộ hệ thống TRM OS và các thành phần liên quan",
            "priority": 1,  # Cao nhất
            "project_type": "strategic",
            "tags": ["strategic", "core", "v3.2", "ontology"],
            "start_date": start_date,
            "target_end_date": target_end_date,
            "health": "good",
            "metrics": {
                "kpi_1": "Đạt 95% mục tiêu",
                "kpi_2": "Đạt 90% tiến độ",
                "budget_effectiveness": 0.85
            },
            "is_strategic": True
        }
        
        logger.info(f"Đang tạo Project chiến lược mới: {project_data['title']}")
        response = requests.post(f"{BASE_URL}/api/projects", headers=HEADERS, json=project_data)
        
        if response.status_code == 200 or response.status_code == 201:
            created_project = response.json()
            logger.info(f"Đã tạo thành công Project chiến lược mới với ID: {created_project.get('uid')}")
            return created_project
        else:
            logger.error(f"Không thể tạo Project: {response.status_code} - {response.text}")
            return None
    except requests.RequestException as e:
        logger.error(f"Lỗi kết nối khi tạo Project: {e}")
        return None

def create_subproject(parent_project_id: str) -> Optional[Dict[str, Any]]:
    """Tạo một Subproject là con của Project đã cho."""
    try:
        start_date = datetime.now().isoformat()
        target_end_date = (datetime.now() + timedelta(days=45)).isoformat()
        
        project_data = {
            "title": f"Dự án Con {uuid.uuid4().hex[:8]}",
            "description": "Một dự án con của dự án chiến lược theo Ontology V3.2",
            "status": "planning",
            "goal": "Hoàn thiện một phần chức năng trong dự án chiến lược cha",
            "scope": "Một phần hệ thống TRM OS",
            "priority": 2,
            "project_type": "implementation",
            "tags": ["subproject", "v3.2", "ontology"],
            "start_date": start_date,
            "target_end_date": target_end_date,
            "health": "normal",
            "metrics": {
                "kpi_1": "Đạt 85% mục tiêu",
                "kpi_2": "Đạt 80% tiến độ"
            },
            "is_strategic": False,
            "parent_project_id": parent_project_id
        }
        
        logger.info(f"Đang tạo Subproject: {project_data['title']} cho Project cha: {parent_project_id}")
        response = requests.post(f"{BASE_URL}/api/projects", headers=HEADERS, json=project_data)
        
        if response.status_code == 200 or response.status_code == 201:
            created_project = response.json()
            logger.info(f"Đã tạo thành công Subproject với ID: {created_project.get('uid')}")
            return created_project
        else:
            logger.error(f"Không thể tạo Subproject: {response.status_code} - {response.text}")
            return None
    except requests.RequestException as e:
        logger.error(f"Lỗi kết nối khi tạo Subproject: {e}")
        return None

def assign_manager_to_project(project_id: str, agent_id: str) -> bool:
    """Thêm mối quan hệ MANAGES_PROJECT giữa Agent và Project."""
    try:
        relationship_data = {
            "role": "project_manager",
            "responsibility_level": "primary",
            "notes": "Quản lý chính của dự án theo Ontology V3.2"
        }
        
        logger.info(f"Đang gán Agent {agent_id} làm manager cho Project {project_id}")
        # Tùy thuộc vào API endpoint đã được triển khai
        response = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/managers/{agent_id}",
            headers=HEADERS, 
            json=relationship_data
        )
        
        if response.status_code == 200 or response.status_code == 201:
            logger.info(f"Đã gán thành công Agent {agent_id} làm manager cho Project {project_id}")
            return True
        else:
            logger.error(f"Không thể gán manager: {response.status_code} - {response.text}")
            return False
    except requests.RequestException as e:
        logger.error(f"Lỗi kết nối khi gán manager: {e}")
        return False

def assign_resource_to_project(project_id: str, resource_id: str) -> bool:
    """Thêm mối quan hệ ASSIGNED_TO_PROJECT giữa Resource và Project."""
    try:
        relationship_data = {
            "allocation_percentage": 75,
            "assignment_type": "part-time",
            "assignment_status": "active",
            "notes": "Tài nguyên được gán cho dự án theo Ontology V3.2"
        }
        
        logger.info(f"Đang gán Resource {resource_id} cho Project {project_id}")
        # Tùy thuộc vào API endpoint đã được triển khai
        response = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/resources/{resource_id}",
            headers=HEADERS, 
            json=relationship_data
        )
        
        if response.status_code == 200 or response.status_code == 201:
            logger.info(f"Đã gán thành công Resource {resource_id} cho Project {project_id}")
            return True
        else:
            logger.error(f"Không thể gán resource: {response.status_code} - {response.text}")
            return False
    except requests.RequestException as e:
        logger.error(f"Lỗi kết nối khi gán resource: {e}")
        return False

def get_project_with_relationships(project_id: str) -> Optional[Dict[str, Any]]:
    """Lấy thông tin đầy đủ về một Project, bao gồm cả relationships."""
    try:
        # Lấy thông tin cơ bản về Project
        response = requests.get(f"{BASE_URL}/api/projects/{project_id}", headers=HEADERS)
        
        if response.status_code != 200:
            logger.error(f"Không thể lấy thông tin Project: {response.status_code} - {response.text}")
            return None
        
        project_data = response.json()
        
        # Lấy danh sách managers (MANAGES_PROJECT)
        managers_response = requests.get(f"{BASE_URL}/api/projects/{project_id}/managers", headers=HEADERS)
        if managers_response.status_code == 200:
            project_data["managers"] = managers_response.json()
        else:
            logger.warning(f"Không thể lấy managers của Project: {managers_response.status_code}")
        
        # Lấy danh sách resources (ASSIGNED_TO_PROJECT)
        resources_response = requests.get(f"{BASE_URL}/api/projects/{project_id}/resources", headers=HEADERS)
        if resources_response.status_code == 200:
            project_data["resources"] = resources_response.json()
        else:
            logger.warning(f"Không thể lấy resources của Project: {resources_response.status_code}")
        
        # Lấy danh sách subprojects
        subprojects_response = requests.get(f"{BASE_URL}/api/projects/{project_id}/subprojects", headers=HEADERS)
        if subprojects_response.status_code == 200:
            project_data["subprojects"] = subprojects_response.json()
        else:
            logger.warning(f"Không thể lấy subprojects của Project: {subprojects_response.status_code}")
        
        return project_data
    except requests.RequestException as e:
        logger.error(f"Lỗi kết nối khi lấy thông tin Project: {e}")
        return None

def verify_project_with_neo4j(project_id: str) -> None:
    """Xác minh dữ liệu Project trực tiếp bằng Cypher query trên Neo4j."""
    # Lưu ý: Phần này sẽ cần được triển khai tùy thuộc vào cách kết nối với Neo4j
    # Hoặc có thể sử dụng endpoint API đặc biệt để thực thi Cypher query
    logger.info(f"Cần triển khai kiểm thử trực tiếp với Neo4j cho Project {project_id}")
    # TODO: Triển khai kiểm thử trực tiếp với Neo4j

def main() -> None:
    """Hàm chính để thực thi seed và kiểm thử."""
    logger.info("Bắt đầu seed và kiểm thử Project với thuộc tính mở rộng theo Ontology V3.2")
    
    # Kiểm tra kết nối đến API server
    if not check_api_health():
        logger.error("Không thể kết nối đến API server. Dừng thực thi.")
        return
    
    # Lấy danh sách users hiện có để làm managers
    users = get_all_users()
    if not users:
        logger.error("Không có User nào để gán làm manager. Dừng thực thi.")
        return
    
    # Lấy danh sách resources hiện có
    resources = get_all_resources()
    if not resources:
        logger.warning("Không có Resource nào để gán cho Project.")
    
    # 1. Tạo một Strategic Project
    strategic_project = create_strategic_project()
    if not strategic_project:
        logger.error("Không thể tạo Strategic Project. Dừng thực thi.")
        return
    
    strategic_project_id = strategic_project.get("uid")
    
    # 2. Tạo một Subproject con của Strategic Project
    subproject = create_subproject(strategic_project_id)
    if not subproject:
        logger.error("Không thể tạo Subproject. Dừng thực thi.")
        return
    
    # 3. Gán manager cho các project
    if users:
        # Gán manager cho Strategic Project
        assign_manager_to_project(strategic_project_id, users[0].get("uid"))
        
        # Nếu có nhiều hơn một user, gán manager khác cho Subproject
        if len(users) > 1:
            assign_manager_to_project(subproject.get("uid"), users[1].get("uid"))
        else:
            assign_manager_to_project(subproject.get("uid"), users[0].get("uid"))
    
    # 4. Gán resources cho các project
    if resources:
        # Gán resource cho Strategic Project
        assign_resource_to_project(strategic_project_id, resources[0].get("uid"))
        
        # Nếu có nhiều hơn một resource, gán resource khác cho Subproject
        if len(resources) > 1:
            assign_resource_to_project(subproject.get("uid"), resources[1].get("uid"))
        else:
            assign_resource_to_project(subproject.get("uid"), resources[0].get("uid"))
    
    # 5. Lấy và hiển thị thông tin đầy đủ về Project để kiểm tra
    logger.info("Lấy thông tin đầy đủ về Strategic Project để kiểm tra...")
    strategic_project_full = get_project_with_relationships(strategic_project_id)
    if strategic_project_full:
        logger.info(json.dumps(strategic_project_full, indent=2))
    
    logger.info("Lấy thông tin đầy đủ về Subproject để kiểm tra...")
    subproject_full = get_project_with_relationships(subproject.get("uid"))
    if subproject_full:
        logger.info(json.dumps(subproject_full, indent=2))
    
    # 6. Xác minh trực tiếp với Neo4j
    # verify_project_with_neo4j(strategic_project_id)
    
    logger.info("Hoàn thành seed và kiểm thử Project với thuộc tính mở rộng theo Ontology V3.2")

if __name__ == "__main__":
    main()
