# Integration Tests cho TRM-OS API

## Cấu trúc và quy trình async testing

Các test tích hợp của TRM-OS được thiết kế dựa trên triết lý ontology-first và async pattern. Tài liệu này cung cấp hướng dẫn về cách tạo, chạy và bảo trì các test này.

### Nguyên tắc thiết kế

1. **Async Pattern**: Tất cả các test đều sử dụng async/await pattern với `pytest-asyncio` và `httpx.AsyncClient`.
2. **Ontology-First**: Mọi response API đều được xác thực chặt chẽ theo cấu trúc ontology.
3. **Tính nhất quán**: Sử dụng fixtures chung để đảm bảo tính nhất quán giữa các test cases.
4. **Isolation**: Mỗi test case đều độc lập, sử dụng UUID mới và mock riêng biệt.

### Cách tạo test integration mới

```python
import pytest
import pytest_asyncio
import uuid
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient

from trm_api.main import app
from tests.conftest import get_test_client

class TestNewFeatureAPI:
    """Integration tests cho API mới."""

    async def setup_method(self):
        """Khởi tạo test fixtures trước mỗi test method."""
        # Tạo các ID mới cho mỗi test
        self.entity_id = str(uuid.uuid4())
        
        # Tạo dữ liệu mẫu
        self.entity_data = {
            "uid": self.entity_id,
            "name": "Test Entity",
            # Thêm thuộc tính khác
        }
        
        # Tạo async client
        self.client = await get_test_client()
    
    @pytest.mark.asyncio
    @patch("trm_api.api.v1.endpoints.example.example_service")
    async def test_create_entity(self, mock_service):
        """Test tạo entity mới."""
        # Setup mock
        mock_service.create_entity = AsyncMock(return_value=self.entity_data)
        
        # Gọi API
        response = await self.client.post("/api/v1/entities/", json=self.entity_data)
        
        # Kiểm tra kết quả
        assert response.status_code == 200
        data = response.json()
        assert data["uid"] == self.entity_id
        
        # Verify mock được gọi
        mock_service.create_entity.assert_called_once()
```

### Cách chạy các test

```bash
# Chạy tất cả các test tích hợp
pytest tests/integration -v

# Chạy một file test cụ thể
pytest tests/integration/test_specific_feature.py -v

# Chạy một test case cụ thể
pytest tests/integration/test_specific_feature.py::TestClass::test_specific_method -v
```

### Best Practices

1. **Luôn dùng async/await**: Tất cả các test và methods phải là async để tránh lỗi "unawaited coroutine".
2. **Dùng AsyncMock thay vì MagicMock**: Cho các service methods được mock.
3. **Sử dụng fixtures**: Luôn dùng `get_test_client()` để có được AsyncClient nhất quán.
4. **Xác thực response**: Luôn kiểm tra cả status code và cấu trúc dữ liệu response theo ontology.
5. **UUID độc lập**: Mỗi test case tạo UUID mới để tránh xung đột dữ liệu.
6. **Reset mocks**: Sử dụng `mock_service.reset_mock()` khi cần test nhiều API calls trong cùng một test.

### Những lỗi thường gặp và cách sửa

1. **Unawaited coroutine detected**: Đảm bảo đã sử dụng `await` trước mọi lời gọi async và đã đánh dấu function với `async`.
2. **AttributeError: 'AsyncMock' object has no attribute 'return_value'**: Sử dụng `mock_service.method = AsyncMock(return_value=...)` thay vì `.return_value = ...`.
3. **TypeError: object dict can't be used in 'await' expression**: Đảm bảo đã sử dụng `httpx.AsyncClient` thay vì `TestClient`.

### Tham khảo

- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)
- [httpx.AsyncClient documentation](https://www.python-httpx.org/async/)
- [unittest.mock.AsyncMock documentation](https://docs.python.org/3/library/unittest.mock.html#unittest.mock.AsyncMock)
