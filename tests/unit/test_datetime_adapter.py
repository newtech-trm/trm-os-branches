import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from trm_api.adapters.datetime_adapter import normalize_datetime, normalize_dict_datetimes

class TestDatetimeAdapter:
    """Unit tests cho datetime_adapter module."""
    
    def test_normalize_datetime_with_none(self):
        """Test normalize_datetime với giá trị None."""
        assert normalize_datetime(None) is None
    
    def test_normalize_datetime_with_neo4j_datetime(self):
        """Test normalize_datetime với Neo4j datetime object."""
        # Tạo mock cho Neo4j datetime object
        neo4j_dt = Mock()
        neo4j_dt.to_native.return_value = datetime(2023, 1, 15, 10, 30, 0)
        
        result = normalize_datetime(neo4j_dt)
        assert result == "2023-01-15T10:30:00"
        neo4j_dt.to_native.assert_called_once()
    
    def test_normalize_datetime_with_neo4j_datetime_error(self):
        """Test normalize_datetime khi Neo4j datetime object lỗi."""
        # Mock Neo4j datetime object nhưng gây ra exception khi gọi to_native()
        neo4j_dt = Mock()
        neo4j_dt.to_native.side_effect = Exception("Neo4j datetime error")
        
        with patch("logging.error") as mock_log:
            result = normalize_datetime(neo4j_dt)
            assert result is None
            mock_log.assert_called_once()
    
    def test_normalize_datetime_with_datetime_object(self):
        """Test normalize_datetime với Python datetime object."""
        dt = datetime(2023, 1, 15, 10, 30, 0)
        result = normalize_datetime(dt)
        assert result == "2023-01-15T10:30:00"
    
    def test_normalize_datetime_with_iso_string(self):
        """Test normalize_datetime với ISO 8601 string."""
        dt_str = "2023-01-15T10:30:00Z"
        result = normalize_datetime(dt_str)
        assert result == "2023-01-15T10:30:00"
    
    def test_normalize_datetime_with_custom_format_string(self):
        """Test normalize_datetime với chuỗi có định dạng tùy chỉnh."""
        dt_str = "2023-01-15 10:30:00"
        result = normalize_datetime(dt_str)
        assert result == "2023-01-15T10:30:00"
    
    def test_normalize_datetime_with_date_only_string(self):
        """Test normalize_datetime với chuỗi chỉ chứa ngày tháng năm."""
        dt_str = "2023-01-15"
        result = normalize_datetime(dt_str)
        assert result == "2023-01-15T00:00:00"
    
    def test_normalize_datetime_with_invalid_string(self):
        """Test normalize_datetime với chuỗi không hợp lệ."""
        dt_str = "not-a-datetime"
        with patch("logging.error") as mock_log:
            result = normalize_datetime(dt_str)
            assert result is None
            mock_log.assert_called_once()
    
    def test_normalize_dict_datetimes_with_none(self):
        """Test normalize_dict_datetimes với giá trị không phải dictionary."""
        assert normalize_dict_datetimes(None) is None
    
    def test_normalize_dict_datetimes_empty_dict(self):
        """Test normalize_dict_datetimes với dictionary rỗng."""
        assert normalize_dict_datetimes({}) == {}
    
    def test_normalize_dict_datetimes_with_datetime_fields(self):
        """Test normalize_dict_datetimes với dictionary chứa trường datetime."""
        dt = datetime(2023, 1, 15, 10, 30, 0)
        data = {
            "id": "123",
            "name": "Test",
            "created_at": dt,
            "updated_at": dt
        }
        
        expected = {
            "id": "123",
            "name": "Test",
            "created_at": "2023-01-15T10:30:00",
            "updated_at": "2023-01-15T10:30:00"
        }
        
        result = normalize_dict_datetimes(data)
        assert result == expected
    
    def test_normalize_dict_datetimes_with_nested_dict(self):
        """Test normalize_dict_datetimes với dictionary lồng nhau."""
        dt = datetime(2023, 1, 15, 10, 30, 0)
        data = {
            "id": "123",
            "name": "Test",
            "metadata": {
                "created_at": dt,
                "other_field": "value"
            }
        }
        
        expected = {
            "id": "123",
            "name": "Test",
            "metadata": {
                "created_at": "2023-01-15T10:30:00",
                "other_field": "value"
            }
        }
        
        result = normalize_dict_datetimes(data)
        assert result == expected
    
    def test_normalize_dict_datetimes_with_list(self):
        """Test normalize_dict_datetimes với dictionary chứa list."""
        dt = datetime(2023, 1, 15, 10, 30, 0)
        data = {
            "id": "123",
            "records": [
                {"id": "1", "created_at": dt},
                {"id": "2", "created_at": dt}
            ]
        }
        
        expected = {
            "id": "123",
            "records": [
                {"id": "1", "created_at": "2023-01-15T10:30:00"},
                {"id": "2", "created_at": "2023-01-15T10:30:00"}
            ]
        }
        
        result = normalize_dict_datetimes(data)
        assert result == expected
