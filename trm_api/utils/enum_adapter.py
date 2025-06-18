"""
Tiện ích chuẩn hóa giá trị enum từ database sang định dạng chuẩn cho API response.
Xử lý các trường hợp không đồng nhất dữ liệu giữa Neo4j và schema Pydantic.

Ontology V3.2 adapter cho các enum và giá trị không nhất quán.
"""
from enum import Enum
from typing import Type, Any, Dict, List, Optional, Union


def normalize_enum_value(value: Any, enum_class: Type[Enum], default=None) -> str:
    """
    Chuẩn hóa giá trị từ database thành giá trị enum hợp lệ.
    
    Args:
        value: Giá trị cần chuẩn hóa từ database
        enum_class: Class enum tham chiếu
        default: Giá trị mặc định nếu không thể chuẩn hóa
        
    Returns:
        Giá trị enum hợp lệ hoặc giá trị mặc định
    """
    # Trường hợp None
    if value is None:
        if default is not None:
            return default
        # Sử dụng giá trị đầu tiên của enum nếu có
        try:
            return list(enum_class)[0].value
        except (IndexError, TypeError):
            return None
    
    # Nếu giá trị đã là enum
    if isinstance(value, enum_class):
        return value.value
    
    # Nếu giá trị là chuỗi
    if isinstance(value, str):
        # Kiểm tra trực tiếp
        valid_values = [e.value for e in enum_class]
        if value in valid_values:
            return value
            
        # Kiểm tra uppercase
        upper_value = value.upper()
        if upper_value in valid_values:
            return upper_value
            
        # Kiểm tra tên đầy đủ của enum (ví dụ: RecognitionType.GRATITUDE)
        if "." in value:
            parts = value.split(".")
            if len(parts) == 2 and parts[1].upper() in valid_values:
                return parts[1].upper()
                
        # Kiểm tra title case (ví dụ: "Gratitude")
        for enum_val in valid_values:
            if value.lower() == enum_val.lower():
                return enum_val
    
    # Trả về giá trị mặc định
    if default is not None:
        return default
        
    # Trả về giá trị đầu tiên của enum
    try:
        return list(enum_class)[0].value
    except (IndexError, TypeError):
        return None


def normalize_object_enums(data: Dict[str, Any], 
                           enum_mapping: Dict[str, Type[Enum]]) -> Dict[str, Any]:
    """
    Chuẩn hóa tất cả giá trị enum trong một đối tượng theo cấu hình.
    
    Args:
        data: Dictionary chứa dữ liệu cần chuẩn hóa
        enum_mapping: Map giữa tên trường và enum class tương ứng
        
    Returns:
        Dictionary với các giá trị enum đã được chuẩn hóa
    """
    result = {}
    
    for key, value in data.items():
        # Nếu là trường cần chuẩn hóa enum
        if key in enum_mapping:
            result[key] = normalize_enum_value(value, enum_mapping[key])
        # Nếu là object con
        elif isinstance(value, dict):
            result[key] = normalize_object_enums(value, enum_mapping)
        # Nếu là danh sách object con
        elif isinstance(value, list) and all(isinstance(x, dict) for x in value):
            result[key] = [normalize_object_enums(item, enum_mapping) for item in value]
        # Các trường hợp còn lại
        else:
            result[key] = value
            
    return result
