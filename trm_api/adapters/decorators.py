import functools
import json
import logging
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime

from fastapi import Response
from fastapi.responses import JSONResponse

from .datetime_adapter import normalize_dict_datetimes


def _process_items(items: Any, adapt_datetime: bool, adapt_enums: Optional[List[Dict[str, Any]]]) -> Any:
    """
    Xử lý và chuẩn hóa các item trong response theo nguyên tắc ontology-first nghiêm ngặt.
    Chuyển đổi tất cả datetime sang chuỗi ISO 8601 và chuẩn hóa enum values.
    
    Args:
        items: Item hoặc danh sách item cần xử lý
        adapt_datetime: Nếu True thì chuẩn hóa các trường datetime
        adapt_enums: Danh sách các adapter để chuẩn hóa enum fields
        
    Returns:
        Dữ liệu đã được chuẩn hóa hoàn toàn theo ontology
    """
    try:
        # Xử lý giá trị None
        if items is None:
            return None
        
        # Xử lý datetime object trực tiếp
        if adapt_datetime and isinstance(items, datetime):
            # Đảm bảo chuyển thành chuỗi ISO 8601
            try:
                return items.isoformat()
            except Exception as e:
                logging.error(f"Error converting datetime to ISO 8601: {e}")
                return str(items)  # Fallback cơ bản nếu có lỗi
        
        # Xử lý danh sách các item
        if isinstance(items, list):
            return [_process_items(item, adapt_datetime, adapt_enums) for item in items]
        
        # Xử lý dictionary
        if isinstance(items, dict):
            result = {}
            # Lưu key của các trường datetime đã biết
            datetime_keys = ['created_at', 'createdat', 'updated_at', 'updatedat', 
                          'start_date', 'startdate', 'end_date', 'enddate', 
                          'due_date', 'duedate', 'target_end_date', 
                          'createdAt', 'updatedAt', 'startDate', 'endDate', 
                          'dueDate', 'targetEndDate']
            
            # Xử lý tất cả các trường trong dictionary
            for key, value in items.items():
                # Xử lý trường hợp datetime đặc biệt
                if adapt_datetime and key in datetime_keys:
                    from .datetime_adapter import normalize_datetime
                    iso_value = normalize_datetime(value)
                    result[key] = iso_value if iso_value is not None else value
                # Xử lý datetime objects trực tiếp
                elif adapt_datetime and isinstance(value, datetime):
                    result[key] = value.isoformat()
                # Xử lý nested dictionaries
                elif isinstance(value, dict):
                    result[key] = _process_items(value, adapt_datetime, adapt_enums)
                # Xử lý nested lists
                elif isinstance(value, list):
                    result[key] = _process_items(value, adapt_datetime, adapt_enums)
                # Sử dụng giá trị nguyên thủy cho các trường hợp khác
                else:
                    result[key] = value
            
            # Xử lý enum fields nếu được yêu cầu
            if adapt_enums:
                for enum_config in adapt_enums:
                    field = enum_config.get("field")
                    adapter = enum_config.get("adapter")
                    if field and field in result and adapter and result[field] is not None:
                        try:
                            normalized_value = adapter(result[field])
                            if normalized_value is not None:
                                result[field] = normalized_value
                        except Exception as e:
                            logging.error(f"Error normalizing enum field '{field}': {e}")
                            # Giữ giá trị gốc nếu có lỗi
            
            return result
        
        # Trả về nguyên giá trị cho các trường hợp khác
        return items
    except Exception as e:
        logging.error(f"Unexpected error in _process_items: {e}")
        return items  # Trả về giá trị gốc nếu có lỗi


def adapt_response(
    response_item_key: Optional[str] = None,
    adapt_datetime: bool = True,
    adapt_enums: Optional[List[Dict[str, Any]]] = None
):
    """
    Decorator chính để chuẩn hóa API response theo triết lý ontology-first nghiêm ngặt.
    Chuyển đổi tất cả datetime sang chuỗi ISO 8601 và chuẩn hóa enum values.
    
    Args:
        response_item_key: Key chứa danh sách các item nếu response là collection
        adapt_datetime: Nếu True thì chuẩn hóa các trường datetime sang ISO format
        adapt_enums: Danh sách các adapter để chuẩn hóa enum fields
            [{'field': 'field_name', 'adapter': normalize_function}]
            
    Returns:
        Decorator function đã được wrap
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Gọi endpoint function gốc
                response = await func(*args, **kwargs)
                
                # Xử lý giá trị None
                if response is None:
                    return None
                
                # Trường hợp response là Response object (FastAPI response)
                if isinstance(response, Response):
                    try:
                        # Chỉ xử lý nếu là JSONResponse
                        if isinstance(response, JSONResponse):
                            # Extract dữ liệu từ response
                            body_content = response.body
                            if isinstance(body_content, bytes):
                                body_content = body_content.decode('utf-8')
                            
                            data = json.loads(body_content)
                            
                            # Xử lý data theo các tham số
                            if response_item_key and isinstance(data, dict) and response_item_key in data:
                                # Chỉ xử lý các mục cụ thể (như 'items')
                                data[response_item_key] = _process_items(
                                    data[response_item_key], adapt_datetime, adapt_enums
                                )
                            else:
                                # Xử lý toàn bộ data
                                data = _process_items(data, adapt_datetime, adapt_enums)
                            
                            # Tạo JSONResponse mới với data đã xử lý
                            return JSONResponse(
                                content=data,
                                status_code=response.status_code,
                                headers=dict(response.headers),
                                media_type=response.media_type,
                            )
                        
                        # Các loại Response khác giữ nguyên
                        return response
                    except Exception as e:
                        logging.error(f"Error processing Response object: {str(e)}")
                        return response
                
                # Trường hợp response là dict hoặc Pydantic model
                if isinstance(response, dict):
                    # Xử lý collection item nếu được chỉ định
                    if response_item_key and response_item_key in response:
                        # Tạo bản sao của response để tránh thay đổi trực tiếp
                        result = dict(response)
                        # Chỉ xử lý collection item được chỉ định
                        result[response_item_key] = _process_items(
                            result[response_item_key], adapt_datetime, adapt_enums
                        )
                        return result
                    
                    # Xử lý toàn bộ dictionary nếu không có response_item_key
                    return _process_items(response, adapt_datetime, adapt_enums)
                
                # Trường hợp response là list hoặc giá trị khác
                return _process_items(response, adapt_datetime, adapt_enums)
            
            except Exception as e:
                # Log lỗi và trả về response gốc trong trường hợp có lỗi ngoài ý muốn
                logging.error(f"Unexpected error in adapt_response decorator: {str(e)}")
                return response
        
        return wrapper
    
    return decorator


def adapt_datetime_response(response_item_key: Optional[str] = None):
    """
    Decorator để tự động chuẩn hóa datetime fields trong response.
    Đảm bảo tất cả datetime objects đều được chuyển thành chuỗi ISO 8601.
    
    Args:
        response_item_key: Key chứa danh sách các item nếu response là collection
        
    Returns:
        Decorator function đã được wrap
    """
    return adapt_response(response_item_key=response_item_key, adapt_datetime=True, adapt_enums=None)


def adapt_win_response(response_item_key: Optional[str] = None):
    """
    Decorator đặc biệt cho WIN API endpoints theo nguyên tắc ontology-first.
    Tự động chuẩn hóa:
    - Các trường datetime sang chuỗi ISO 8601
    - Trường 'status' sang dạng enum chuẩn ontology
    - Trường 'winType' sang dạng enum chuẩn ontology
    
    Args:
        response_item_key: Key chứa danh sách các item nếu response là collection
        
    Returns:
        Decorator function đã được wrap
    """
    # Import lazy để tránh circular dependency
    from .enum_adapter import normalize_win_status, normalize_win_type
    
    return adapt_response(
        response_item_key=response_item_key,
        adapt_datetime=True,
        adapt_enums=[
            {"field": "status", "adapter": normalize_win_status},
            {"field": "winType", "adapter": normalize_win_type}
        ]
    )


def adapt_recognition_response(response_item_key: Optional[str] = None):
    """
    Decorator đặc biệt cho Recognition API endpoints theo nguyên tắc ontology-first.
    Tự động chuẩn hóa:
    - Các trường datetime sang chuỗi ISO 8601
    - Trường 'status' sang dạng enum chuẩn ontology
    - Trường 'recognitionType' sang dạng enum chuẩn ontology
    
    Args:
        response_item_key: Key chứa danh sách các item nếu response là collection
        
    Returns:
        Decorator function đã được wrap
    """
    # Import lazy để tránh circular dependency
    from .enum_adapter import normalize_recognition_type, normalize_recognition_status
    
    return adapt_response(
        response_item_key=response_item_key,
        adapt_datetime=True,
        adapt_enums=[
            {"field": "status", "adapter": normalize_recognition_status},
            {"field": "recognitionType", "adapter": normalize_recognition_type}
        ]
    )
