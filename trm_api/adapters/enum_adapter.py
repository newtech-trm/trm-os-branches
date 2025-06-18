import logging
from typing import Optional, Dict, Any, Union

def normalize_enum_value(value: Optional[str], enum_choices: Dict[str, str], default: Optional[str] = None) -> Optional[str]:
    """
    Chuẩn hóa giá trị enum từ nhiều dạng khác nhau sang dạng chuẩn của enum.
    
    Args:
        value: Giá trị enum cần chuẩn hóa (có thể là None)
        enum_choices: Dictionary chứa các giá trị enum hợp lệ (key là giá trị chuẩn, value là label)
        default: Giá trị mặc định nếu không tìm thấy kết quả phù hợp
        
    Returns:
        Giá trị enum đã chuẩn hóa hoặc default nếu không tìm thấy
    """
    if value is None:
        return default
    
    # Chuẩn hóa value thành lowercase và loại bỏ dấu cách
    normalized_input = str(value).lower().strip()
    
    # Case 1: Value đã đúng định dạng chuẩn (key của enum_choices)
    if normalized_input in enum_choices:
        return normalized_input
    
    # Case 2: Value tương ứng với một trong các label (value của enum_choices)
    for enum_key, enum_label in enum_choices.items():
        if normalized_input == enum_label.lower():
            return enum_key
    
    # Case 3: Value trùng với một phần của key hoặc label
    for enum_key, enum_label in enum_choices.items():
        if normalized_input in enum_key.lower() or normalized_input in enum_label.lower():
            logging.warning(f"Fuzzy matching enum value '{value}' to '{enum_key}'")
            return enum_key
    
    # Case 4: Không tìm thấy kết quả phù hợp, trả về default hoặc giá trị gốc
    if default is not None:
        logging.warning(f"Could not normalize enum value '{value}', using default: '{default}'")
        return default
    
    logging.warning(f"Could not normalize enum value '{value}', returning as is")
    return value

def normalize_win_status(status: Optional[str]) -> Optional[str]:
    """
    Chuẩn hóa trạng thái của WIN theo ontology.
    """
    WIN_STATUS_CHOICES = {
        "draft": "Draft",
        "under_review": "Under Review",
        "published": "Published",
        "archived": "Archived",
    }
    return normalize_enum_value(status, WIN_STATUS_CHOICES, "draft")

def normalize_win_type(win_type: Optional[str]) -> Optional[str]:
    """
    Chuẩn hóa loại WIN theo ontology.
    """
    WIN_TYPE_CHOICES = {
        "problem_resolution": "Problem Resolution",
        "insight_discovery": "Insight Discovery",
        "process_optimization": "Process Optimization",
        "learning_milestone": "Learning Milestone",
        "strategic_achievement": "Strategic Achievement",
    }
    return normalize_enum_value(win_type, WIN_TYPE_CHOICES, None)

def normalize_recognition_type(recognition_type: Optional[str]) -> Optional[str]:
    """
    Chuẩn hóa loại Recognition theo ontology.
    """
    RECOGNITION_TYPE_CHOICES = {
        "kudos": "Kudos",
        "appreciation": "Appreciation",
        "celebration": "Celebration",
        "achievement": "Achievement",
        "milestone": "Milestone",
        "breakthrough": "Breakthrough"
    }
    return normalize_enum_value(recognition_type, RECOGNITION_TYPE_CHOICES, None)

def normalize_recognition_status(status: Optional[str]) -> Optional[str]:
    """
    Chuẩn hóa trạng thái Recognition theo ontology.
    """
    RECOGNITION_STATUS_CHOICES = {
        "draft": "Draft",
        "published": "Published",
        "acknowledged": "Acknowledged",
        "archived": "Archived"
    }
    return normalize_enum_value(status, RECOGNITION_STATUS_CHOICES, "draft")
