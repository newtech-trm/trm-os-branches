import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import uuid

from trm_api.main import app
from trm_api.schemas.recognition import RecognitionCreate, RecognitionType, RecognitionStatus


@pytest.fixture
def client():
    return TestClient(app)


def test_create_recognition(client):
    """
    Test creating a new recognition and verify the response structure and datetime handling.
    """
    # Tạo dữ liệu cho recognition mới
    recognition_data = {
        "name": "Test Recognition",
        "message": "Công nhận đóng góp tuyệt vời",
        "recognition_type": "GRATITUDE", # Phải khớp với enum RecognitionType
        "status": "GRANTED", # Phải khớp với enum RecognitionStatus  
        "value_level": "3", # string thay vì integer
        "tags": ["test", "api"],
        "given_by_agent_id": f"test_{str(uuid.uuid4())}",
        "received_by_agent_ids": [f"test_{str(uuid.uuid4())}", f"test_{str(uuid.uuid4())}"],
        "recognizes_win_id": None,
        "recognizes_contributions": {
            "project": [f"test_{str(uuid.uuid4())}"],
            "task": [f"test_{str(uuid.uuid4())}"],
            "resource": []
        }
    }
    
    # Gọi API tạo recognition
    response = client.post("/api/v1/recognitions/", json=recognition_data)
    
    # Kiểm tra response status code
    assert response.status_code == 201
    
    # Kiểm tra response body và cấu trúc
    response_data = response.json()
    
    # Kiểm tra id field
    assert "id" in response_data
    assert isinstance(response_data["id"], str)
    
    # Kiểm tra các trường cơ bản
    assert response_data["name"] == recognition_data["name"]
    assert response_data["message"] == recognition_data["message"]
    assert response_data["recognition_type"] == recognition_data["recognition_type"]
    assert response_data["status"] == recognition_data["status"]
    assert response_data["value_level"] == recognition_data["value_level"]
    assert set(response_data["tags"]) == set(recognition_data["tags"])
    
    # Kiểm tra datetime fields
    assert "created_at" in response_data
    assert "updated_at" in response_data
    
    # Kiểm tra định dạng datetime ISO 8601
    try:
        datetime.fromisoformat(response_data["created_at"].replace("Z", "+00:00"))
        datetime.fromisoformat(response_data["updated_at"].replace("Z", "+00:00"))
    except ValueError:
        pytest.fail("Datetime fields không đúng định dạng ISO 8601")


def test_get_recognition(client):
    """
    Kiểm thử việc lấy thông tin recognition.
    """
    # Trước tiên, tạo một recognition
    recognition_data = {
        "name": "Test Get Recognition",
        "message": "Kiểm thử lấy thông tin",
        "recognition_type": "GRATITUDE",
        "status": "GRANTED",
        "value_level": "2",
        "tags": ["get", "test"],
        "given_by_agent_id": f"test_{str(uuid.uuid4())}",
        "received_by_agent_ids": [f"test_{str(uuid.uuid4())}"]
    }
    
    # Tạo recognition trước
    create_response = client.post("/api/v1/recognitions/", json=recognition_data)
    assert create_response.status_code == 201
    
    # Lấy ID của recognition vừa tạo
    recognition_id = create_response.json()["id"]
    
    # Gọi API get recognition
    response = client.get(f"/api/v1/recognitions/{recognition_id}")
    
    # Kiểm tra response
    assert response.status_code == 200
    
    # Kiểm tra dữ liệu
    response_data = response.json()
    assert response_data["id"] == recognition_id
    assert response_data["name"] == recognition_data["name"]
    
    # Kiểm tra datetime adapter
    assert "created_at" in response_data
    assert "updated_at" in response_data
    try:
        datetime.fromisoformat(response_data["created_at"].replace("Z", "+00:00"))
    except ValueError:
        pytest.fail("created_at field không đúng định dạng ISO 8601")


def test_list_recognitions(client):
    """
    Kiểm thử việc lấy danh sách recognition.
    """
    # Tạo một vài recognition để test
    for i in range(3):
        recognition_data = {
            "name": f"Test List Recognition {i}",
            "message": f"Kiểm thử danh sách {i}",
            "recognition_type": "GRATITUDE",
            "status": "GRANTED",
            "value_level": str(i + 1),
            "tags": ["list", "test", f"item{i}"],
            "given_by_agent_id": f"test_{str(uuid.uuid4())}",
            "received_by_agent_ids": [f"test_{str(uuid.uuid4())}"]
        }
        
        # Tạo recognition
        client.post("/api/v1/recognitions/", json=recognition_data)
    
    # Gọi API list với pagination
    response = client.get("/api/v1/recognitions/?skip=0&limit=10")
    
    # Kiểm tra response
    assert response.status_code == 200
    
    # Kiểm tra cấu trúc response
    response_data = response.json()
    assert "items" in response_data
    assert "total" in response_data
    assert "skip" in response_data
    assert "limit" in response_data
    
    # Kiểm tra số lượng item (ít nhất phải có những item vừa tạo)
    assert len(response_data["items"]) >= 3
    
    # Kiểm tra cấu trúc và datetime của từng item
    for item in response_data["items"]:
        assert "id" in item
        assert "name" in item
        assert "created_at" in item
        try:
            datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
        except ValueError:
            pytest.fail("created_at field không đúng định dạng ISO 8601")


def test_update_recognition(client):
    """
    Kiểm thử việc cập nhật recognition và đảm bảo datetime adapter hoạt động đúng.
    """
    # Tạo recognition
    recognition_data = {
        "name": "Test Update Recognition",
        "message": "Kiểm thử cập nhật",
        "recognition_type": "GRATITUDE",
        "status": "GRANTED",
        "value_level": "4",
        "tags": ["update", "test"],
        "given_by_agent_id": f"test_{str(uuid.uuid4())}",
        "received_by_agent_ids": [f"test_{str(uuid.uuid4())}"]
    }
    
    # Tạo recognition
    create_response = client.post("/api/v1/recognitions/", json=recognition_data)
    assert create_response.status_code == 201
    
    # Lấy ID
    recognition_id = create_response.json()["id"]
    
    # Lưu lại thời gian tạo ban đầu
    initial_created_at = create_response.json()["created_at"]
    
    # Dữ liệu cập nhật
    update_data = {
        "name": "Updated Recognition Name",
        "message": "Đã cập nhật thông tin",
        "value_level": "5",
        "tags": ["updated", "test"]
    }
    
    # Gọi API cập nhật
    update_response = client.put(f"/api/v1/recognitions/{recognition_id}", json=update_data)
    
    # Kiểm tra response
    assert update_response.status_code == 200
    
    # Kiểm tra dữ liệu đã cập nhật
    response_data = update_response.json()
    assert response_data["name"] == update_data["name"]
    assert response_data["message"] == update_data["message"]
    assert response_data["value_level"] == update_data["value_level"]
    assert set(response_data["tags"]) == set(update_data["tags"])
    
    # Kiểm tra created_at không đổi
    assert response_data["created_at"] == initial_created_at
    
    # Kiểm tra updated_at đã thay đổi và theo đúng định dạng ISO
    assert response_data["updated_at"] != initial_created_at
    try:
        datetime.fromisoformat(response_data["updated_at"].replace("Z", "+00:00"))
    except ValueError:
        pytest.fail("updated_at field không đúng định dạng ISO 8601")


def test_delete_recognition(client):
    """
    Kiểm thử việc xóa recognition.
    """
    # Tạo recognition
    recognition_data = {
        "name": "Test Delete Recognition",
        "message": "Kiểm thử xóa",
        "recognition_type": "GRATITUDE",
        "status": "GRANTED",
        "value_level": "1",
        "tags": ["delete", "test"],
        "given_by_agent_id": f"test_{str(uuid.uuid4())}",
        "received_by_agent_ids": [f"test_{str(uuid.uuid4())}"]
    }
    
    # Tạo recognition
    create_response = client.post("/api/v1/recognitions/", json=recognition_data)
    assert create_response.status_code == 201
    
    # Lấy ID
    recognition_id = create_response.json()["id"]
    
    # Gọi API xóa
    delete_response = client.delete(f"/api/v1/recognitions/{recognition_id}")
    
    # Kiểm tra response
    assert delete_response.status_code == 204
    
    # Kiểm tra recognition đã bị xóa bằng cách thử get lại
    get_response = client.get(f"/api/v1/recognitions/{recognition_id}")
    assert get_response.status_code == 404
