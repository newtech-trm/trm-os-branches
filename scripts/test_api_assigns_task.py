#!/usr/bin/env python3
"""
Script kiểm thử API endpoints cho mối quan hệ ASSIGNS_TASK giữa User/Agent và Task.
Sử dụng HTTP requests trực tiếp để tương tác với API endpoints.
"""
import sys
import os
import uuid
import json
import requests
from datetime import datetime

# API Base URL - Điều chỉnh nếu API đang chạy trên cổng khác
API_BASE_URL = "http://localhost:8000/api/v1"

def print_header(message):
    """In tiêu đề cho các bước kiểm thử."""
    print("\n" + "=" * 80)
    print(f" {message.upper()} ".center(80, "="))
    print("=" * 80)

def create_user():
    """Tạo User mới thông qua API để thực hiện kiểm thử."""
    print_header("Tạo user mới")
    
    user_data = {
        "username": f"test_user_{uuid.uuid4().hex[:8]}",
        "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
        "full_name": "Test User",
        "password": "StrongPassword123!"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/users/", json=user_data)
        response.raise_for_status()  # Raise exception cho HTTP error
        user = response.json()
        print(f"Đã tạo User: {user['username']} (UID: {user['uid']})")
        return user
    except Exception as e:
        print(f"Lỗi khi tạo User: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return None

def create_project():
    """Tạo Project mới thông qua API."""
    print_header("Tạo project mới")
    
    project_data = {
        "title": f"Test Project {uuid.uuid4().hex[:8]}",
        "description": "Dự án kiểm thử mối quan hệ ASSIGNS_TASK từ API",
        "status": "active"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/projects/", json=project_data)
        response.raise_for_status()
        project = response.json()
        print(f"Đã tạo Project: {project['title']} (UID: {project['uid']})")
        return project
    except Exception as e:
        print(f"Lỗi khi tạo Project: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return None

def create_task(project_id):
    """Tạo Task mới thông qua API."""
    print_header("Tạo task mới")
    
    task_data = {
        "name": f"Test Task {uuid.uuid4().hex[:8]}",
        "description": "Task kiểm thử mối quan hệ ASSIGNS_TASK từ API",
        "status": "todo",
        "effort": 2,
        "project_id": project_id
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/tasks/", json=task_data)
        response.raise_for_status()
        task = response.json()
        print(f"Đã tạo Task: {task['name']} (UID: {task['uid']})")
        return task
    except Exception as e:
        print(f"Lỗi khi tạo Task: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return None

def assign_task_to_user(task_id, user_id):
    """Tạo mối quan hệ ASSIGNS_TASK từ User đến Task."""
    print_header("Gán Task cho User (ASSIGNS_TASK)")
    
    try:
        # Thiết lập mối quan hệ ASSIGNS_TASK
        response = requests.post(
            f"{API_BASE_URL}/tasks/{task_id}/assign/user/{user_id}",
            params={
                "assignment_type": "Primary",
                "priority_level": 2,
                "estimated_effort": 5.5,
                "notes": "Kiểm thử mối quan hệ ASSIGNS_TASK từ API"
            }
        )
        response.raise_for_status()
        relationship = response.json()
        print(f"Kết quả gán nhiệm vụ từ API:")
        print(json.dumps(relationship, indent=2))
        return True
    except Exception as e:
        print(f"Lỗi khi gán Task cho User: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return False

def get_task_assignees(task_id, include_details=False):
    """Lấy danh sách người được gán cho Task."""
    print_header(f"Lấy danh sách assignees cho Task (details={include_details})")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/tasks/{task_id}/assignees",
            params={"include_relationship_details": include_details}
        )
        response.raise_for_status()
        assignees = response.json()
        print(f"Task có {len(assignees.get('users', []))} người dùng và {len(assignees.get('agents', []))} agent được gán:")
        
        if include_details:
            # In kết quả chi tiết nhưng bỏ qua một số trường để dễ đọc hơn
            for idx, user_data in enumerate(assignees.get('users', []), 1):
                user = user_data.get('user', {})
                rel = user_data.get('relationship', {})
                print(f"  {idx}. User: {user.get('username')} (UID: {user.get('uid')})")
                print(f"     Relationship: type={rel.get('assignmentType')}, priority={rel.get('priorityLevel')}")
        else:
            # In kết quả đơn giản hơn
            for idx, user in enumerate(assignees.get('users', []), 1):
                print(f"  {idx}. User: {user.get('username')} (UID: {user.get('uid')})")
                
        return assignees
    except Exception as e:
        print(f"Lỗi khi lấy danh sách assignees: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return {"users": [], "agents": []}

def accept_task_assignment(task_id, user_id):
    """Chấp nhận nhiệm vụ được gán."""
    print_header(f"Chấp nhận Task")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/tasks/{task_id}/accept",
            params={
                "assignee_id": user_id,
                "acceptance_notes": "Chấp nhận nhiệm vụ từ API test"
            }
        )
        response.raise_for_status()
        result = response.json()
        print(f"Kết quả chấp nhận nhiệm vụ từ API:")
        print(json.dumps(result, indent=2))
        return True
    except Exception as e:
        print(f"Lỗi khi chấp nhận nhiệm vụ: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return False

def complete_task_assignment(task_id, user_id):
    """Đánh dấu hoàn thành nhiệm vụ được gán."""
    print_header(f"Đánh dấu hoàn thành Task")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/tasks/{task_id}/complete",
            params={
                "assignee_id": user_id,
                "actual_effort": 6.5
            }
        )
        response.raise_for_status()
        result = response.json()
        print(f"Kết quả đánh dấu hoàn thành nhiệm vụ từ API:")
        print(json.dumps(result, indent=2))
        return True
    except Exception as e:
        print(f"Lỗi khi đánh dấu hoàn thành nhiệm vụ: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return False

def remove_task_assignment(task_id, user_id):
    """Xóa mối quan hệ ASSIGNS_TASK giữa User và Task."""
    print_header("Xóa gán nhiệm vụ")
    
    try:
        response = requests.delete(
            f"{API_BASE_URL}/tasks/{task_id}/assignment/{user_id}"
        )
        response.raise_for_status()
        print(f"Đã xóa mối quan hệ ASSIGNS_TASK giữa Task {task_id} và User {user_id}")
        return True
    except Exception as e:
        print(f"Lỗi khi xóa mối quan hệ ASSIGNS_TASK: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return False

def delete_task(task_id):
    """Xóa Task đã tạo."""
    print_header("Xóa Task")
    
    try:
        response = requests.delete(f"{API_BASE_URL}/tasks/{task_id}")
        response.raise_for_status()
        print(f"Đã xóa Task (UID: {task_id})")
        return True
    except Exception as e:
        print(f"Lỗi khi xóa Task: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return False

def delete_project(project_id):
    """Xóa Project đã tạo."""
    print_header("Xóa Project")
    
    try:
        response = requests.delete(f"{API_BASE_URL}/projects/{project_id}")
        response.raise_for_status()
        print(f"Đã xóa Project (UID: {project_id})")
        return True
    except Exception as e:
        print(f"Lỗi khi xóa Project: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return False

def delete_user(user_id):
    """Xóa User đã tạo."""
    print_header("Xóa User")
    
    try:
        response = requests.delete(f"{API_BASE_URL}/users/{user_id}")
        response.raise_for_status()
        print(f"Đã xóa User (UID: {user_id})")
        return True
    except Exception as e:
        print(f"Lỗi khi xóa User: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return False

def cleanup(user_id, project_id, task_id):
    """Dọn dẹp dữ liệu kiểm thử."""
    print_header("Dọn dẹp dữ liệu kiểm thử")
    
    # Xóa mối quan hệ trước
    remove_task_assignment(task_id, user_id)
    
    # Xóa các node theo thứ tự
    task_deleted = delete_task(task_id)
    project_deleted = delete_project(project_id)
    user_deleted = delete_user(user_id)
    
    if task_deleted and project_deleted and user_deleted:
        print("Đã dọn dẹp xong dữ liệu kiểm thử")
        return True
    else:
        print(f"Có vấn đề khi dọn dẹp dữ liệu. " + 
              f"Task deleted: {task_deleted}, " + 
              f"Project deleted: {project_deleted}, " + 
              f"User deleted: {user_deleted}")
        return False

def main():
    """Hàm main thực hiện các bước kiểm thử."""
    print_header("BẮT ĐẦU KIỂM THỬ API MỐI QUAN HỆ ASSIGNS_TASK")
    print(f"Thời gian bắt đầu: {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
    
    try:
        # Kiểm tra trạng thái API server
        print("Kiểm tra kết nối tới API server...")
        try:
            # Thay vì kiểm tra endpoint /docs, kiểm tra endpoint /api/v1/users
            response = requests.get(f"{API_BASE_URL}/users")
            print(f"API server sẵn sàng, status code: {response.status_code}")
            # Tiếp tục ngay cả khi status code không phải 200
        except Exception as e:
            print(f"Không thể kết nối tới API server: {e}")
            print("Đảm bảo TRM API server đang chạy trước khi thực hiện kiểm thử.")
            return
        
        # Bước 1: Tạo User, Project và Task mới
        user = create_user()
        if not user:
            return
        
        project = create_project()
        if not project:
            delete_user(user["uid"])
            return
        
        task = create_task(project["uid"])
        if not task:
            delete_project(project["uid"])
            delete_user(user["uid"])
            return
        
        # Bước 2: Tạo mối quan hệ ASSIGNS_TASK
        if assign_task_to_user(task["uid"], user["uid"]):
            # Bước 3: Kiểm tra mối quan hệ
            assignees = get_task_assignees(task["uid"], include_details=False)
            assignees_detailed = get_task_assignees(task["uid"], include_details=True)
            
            # Xác minh mối quan hệ đã được tạo đúng
            user_found = False
            for u in assignees.get('users', []):
                if u.get('uid') == user["uid"]:
                    user_found = True
                    break
            
            if user_found:
                print("\n✓ Mối quan hệ ASSIGNS_TASK đã được tạo thành công")
            else:
                print("\n✗ Mối quan hệ ASSIGNS_TASK không được tạo")
            
            # Bước 4: Kiểm thử chấp nhận nhiệm vụ
            if accept_task_assignment(task["uid"], user["uid"]):
                print("\n✓ Chấp nhận nhiệm vụ thành công")
                
                # Kiểm tra lại trạng thái sau khi chấp nhận
                assignees_after_accept = get_task_assignees(task["uid"], include_details=True)
                
                # Bước 5: Kiểm thử hoàn thành nhiệm vụ
                if complete_task_assignment(task["uid"], user["uid"]):
                    print("\n✓ Đánh dấu hoàn thành nhiệm vụ thành công")
                    
                    # Kiểm tra lại trạng thái sau khi hoàn thành
                    assignees_after_complete = get_task_assignees(task["uid"], include_details=True)
                
            # Bước 6: Xóa mối quan hệ
            if remove_task_assignment(task["uid"], user["uid"]):
                print("✓ Mối quan hệ đã được xóa thành công")
                
                # Kiểm tra lại sau khi xóa
                assignees_after_remove = get_task_assignees(task["uid"])
                if not assignees_after_remove.get('users'):
                    print("✓ Xác nhận mối quan hệ đã xóa thành công")
                else:
                    print("✗ Mối quan hệ vẫn còn tồn tại sau khi xóa")
        
        # Bước 7: Dọn dẹp
        cleanup(user["uid"], project["uid"], task["uid"])
        
        print_header("KIỂM THỬ HOÀN THÀNH")
        print(f"Thời gian kết thúc: {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
        
    except Exception as e:
        print(f"\nLỖI TRONG QUÁ TRÌNH KIỂM THỬ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
