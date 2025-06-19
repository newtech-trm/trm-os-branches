import pytest
from unittest.mock import patch

from trm_api.adapters.enum_adapter import (
    normalize_enum_value,
    normalize_win_status,
    normalize_win_type,
    normalize_recognition_type,
    normalize_recognition_status
)

class TestEnumAdapter:
    """Unit tests cho enum_adapter module."""
    
    def test_normalize_enum_value_with_none(self):
        """Test normalize_enum_value với giá trị None."""
        enum_choices = {"active": "Active", "inactive": "Inactive"}
        default = "active"
        
        result = normalize_enum_value(None, enum_choices, default)
        assert result == default
    
    def test_normalize_enum_value_with_exact_key(self):
        """Test normalize_enum_value với key chính xác."""
        enum_choices = {"active": "Active", "inactive": "Inactive"}
        
        result = normalize_enum_value("active", enum_choices)
        assert result == "active"
    
    def test_normalize_enum_value_with_exact_label(self):
        """Test normalize_enum_value với label chính xác."""
        enum_choices = {"active": "Active", "inactive": "Inactive"}
        
        result = normalize_enum_value("Active", enum_choices)
        assert result == "active"
    
    def test_normalize_enum_value_case_insensitive(self):
        """Test normalize_enum_value không phân biệt hoa thường."""
        enum_choices = {"active": "Active", "inactive": "Inactive"}
        
        result = normalize_enum_value("ACTIVE", enum_choices)
        assert result == "active"
        
        result = normalize_enum_value("active", enum_choices)
        assert result == "active"
    
    def test_normalize_enum_value_fuzzy_matching(self):
        """Test normalize_enum_value với fuzzy matching."""
        enum_choices = {"in_progress": "In Progress", "completed": "Completed"}
        
        with patch("logging.warning") as mock_log:
            result = normalize_enum_value("progress", enum_choices)
            assert result == "in_progress"
            mock_log.assert_called_once()
    
    def test_normalize_enum_value_default(self):
        """Test normalize_enum_value trả về default khi không tìm thấy kết quả phù hợp."""
        enum_choices = {"active": "Active", "inactive": "Inactive"}
        default = "active"
        
        with patch("logging.warning") as mock_log:
            result = normalize_enum_value("unknown", enum_choices, default)
            assert result == default
            mock_log.assert_called_once()
    
    def test_normalize_enum_value_no_default(self):
        """Test normalize_enum_value trả về giá trị gốc khi không có default và không tìm thấy kết quả phù hợp."""
        enum_choices = {"active": "Active", "inactive": "Inactive"}
        
        with patch("logging.warning") as mock_log:
            result = normalize_enum_value("unknown", enum_choices)
            assert result == "unknown"
            mock_log.assert_called_once()
    
    def test_normalize_win_status(self):
        """Test normalize_win_status với các trường hợp phổ biến."""
        # Giá trị chính xác
        assert normalize_win_status("draft") == "draft"
        assert normalize_win_status("published") == "published"
        
        # Giá trị tương tự
        assert normalize_win_status("PUBLISHED") == "published"
        assert normalize_win_status("Under Review") == "under_review"
        
        # Giá trị không hợp lệ
        assert normalize_win_status(None) == "draft"  # default
        assert normalize_win_status("unknown") == "draft"  # default
    
    def test_normalize_win_type(self):
        """Test normalize_win_type với các trường hợp phổ biến."""
        # Giá trị chính xác
        assert normalize_win_type("problem_resolution") == "problem_resolution"
        assert normalize_win_type("insight_discovery") == "insight_discovery"
        
        # Giá trị tương tự
        assert normalize_win_type("Problem Resolution") == "problem_resolution"
        assert normalize_win_type("INSIGHT") == "insight_discovery"
        
        # Giá trị không hợp lệ
        assert normalize_win_type(None) is None  # no default
        
        # Fuzzy matching
        with patch("logging.warning"):
            assert normalize_win_type("problem") == "problem_resolution"
    
    def test_normalize_recognition_type(self):
        """Test normalize_recognition_type với các trường hợp phổ biến."""
        # Giá trị chính xác
        assert normalize_recognition_type("kudos") == "kudos"
        assert normalize_recognition_type("appreciation") == "appreciation"
        
        # Giá trị tương tự
        assert normalize_recognition_type("Kudos") == "kudos"
        assert normalize_recognition_type("APPRECIATION") == "appreciation"
        
        # Giá trị không hợp lệ
        assert normalize_recognition_type(None) is None  # no default
    
    def test_normalize_recognition_status(self):
        """Test normalize_recognition_status với các trường hợp phổ biến."""
        # Giá trị chính xác
        assert normalize_recognition_status("draft") == "draft"
        assert normalize_recognition_status("published") == "published"
        
        # Giá trị tương tự
        assert normalize_recognition_status("Draft") == "draft"
        assert normalize_recognition_status("PUBLISHED") == "published"
        
        # Giá trị không hợp lệ
        assert normalize_recognition_status(None) == "draft"  # default
        assert normalize_recognition_status("unknown") == "draft"  # default
