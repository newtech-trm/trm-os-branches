import logging
from typing import Optional, Dict, Any, Union
from datetime import datetime

def normalize_datetime(dt_value: Any) -> Optional[str]:
    """
    Chuẩn hóa giá trị datetime thành chuỗi ISO 8601.
    
    Args:
        dt_value: Giá trị datetime từ Neo4j hoặc nguồn khác
        
    Returns:
        Chuỗi ISO 8601 hoặc None nếu không thể chuẩn hóa
    """
    if dt_value is None:
        return None
        
    # Nếu đã có phương thức to_native (Neo4j datetime)
    if hasattr(dt_value, 'to_native'):
        try:
            dt_value = dt_value.to_native()
            logging.debug(f"Converted Neo4j DateTime to native: {dt_value}")
        except Exception as e:
            logging.error(f"Error converting Neo4j DateTime: {e}")
            return None
    
    # Chuyển đổi chuỗi sang datetime nếu cần
    if isinstance(dt_value, str):
        try:
            # Thử parse nhiều định dạng khác nhau
            for fmt in ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                try:
                    dt_value = datetime.strptime(dt_value, fmt)
                    break
                except ValueError:
                    continue
        except Exception as e:
            logging.error(f"Error parsing datetime string '{dt_value}': {e}")
            return None
    
    # Nếu không phải datetime object sau tất cả các chuyển đổi
    if not isinstance(dt_value, datetime):
        logging.error(f"Value is not a datetime object after conversions: {dt_value} ({type(dt_value)})")
        return None
    
    # Chuyển thành chuỗi ISO 8601
    try:
        return dt_value.isoformat()
    except Exception as e:
        logging.error(f"Error converting datetime to ISO format: {e}")
        return None

def normalize_dict_datetimes(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Chuẩn hóa tất cả các trường datetime trong một dictionary.
    
    Args:
        data: Dictionary cần xử lý
        
    Returns:
        Dictionary với các trường datetime đã được chuẩn hóa
    """
    if not isinstance(data, dict):
        return data
        
    result = {}
    for key, value in data.items():
        # Xử lý các trường thường là datetime
        if key in ['created_at', 'updated_at', 'start_date', 'end_date', 'due_date', 'target_end_date']:
            result[key] = normalize_datetime(value)
        # Xử lý các giá trị là dict
        elif isinstance(value, dict):
            result[key] = normalize_dict_datetimes(value)
        # Xử lý các giá trị là list
        elif isinstance(value, list):
            result[key] = [
                normalize_dict_datetimes(item) if isinstance(item, dict) else item 
                for item in value
            ]
        # Các giá trị khác giữ nguyên
        else:
            result[key] = value
            
    return result
