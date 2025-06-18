import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import uuid

from trm_api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_simple_recognition(client):
    """
    Test tối thiểu chỉ tạo Recognition với các trường bắt buộc và không có relationship.
    """
    # Tạo dữ liệu tối thiểu cho recognition với các trường bắt buộc
    recognition_data = {
        "name": "Simple Test Recognition",
        "message": "Test đơn giản để xác định lỗi",
        "recognition_type": "GRATITUDE", 
        "status": "GRANTED",
        "given_by_agent_id": f"test_{str(uuid.uuid4())}",
        "received_by_agent_ids": [f"test_{str(uuid.uuid4())}"],
        "value_level": "3"
    }
    
    # Gọi API tạo recognition
    response = client.post("/api/v1/recognitions/", json=recognition_data)
    
    # In response để debug
    print("Response status code:", response.status_code)
    print("Response body:", response.json() if response.status_code != 500 else "Internal Server Error")
    
    # Kiểm tra response status code
    assert response.status_code == 201
