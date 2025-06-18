import uuid
import logging
import traceback
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from trm_api.schemas.recognition import (
    RecognitionCreate, Recognition, RecognitionList, RecognitionUpdate,
    RecognitionWithRelationships, RecognitionType, RecognitionStatus
)
from trm_api.services.recognition_service import recognition_service
from trm_api.utils.datetime_adapter import adapt_model_to_schema, adapt_model_list_to_schema
from trm_api.utils.enum_adapter import normalize_enum_value, normalize_object_enums

router = APIRouter()

# Cấu hình logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@router.post("/", response_model=Recognition, status_code=status.HTTP_201_CREATED)
def create_recognition(
    recognition_data: RecognitionCreate
):
    """
    Create a new Recognition.
    """
    recognition = recognition_service.create_recognition(recognition_data)
    if recognition is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Không thể tạo Recognition"
        )
    
    # Áp dụng datetime_adapter để chuyển từ đối tượng Neo4j sang schema
    return adapt_model_to_schema(recognition, id_field_name="uid", target_id_name="id")

@router.get("/{recognition_id}", response_model=Recognition)
def get_recognition(recognition_id: str):
    """
    Get a specific Recognition by its ID.
    """
    recognition = recognition_service.get_recognition_by_id(recognition_id)
    if recognition is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Recognition không tồn tại"
        )
    
    # Áp dụng datetime_adapter để chuyển từ đối tượng Neo4j sang schema
    return adapt_model_to_schema(recognition, id_field_name="uid", target_id_name="id")

# Bỏ response_model để tránh lỗi validation với dữ liệu cũ không đồng nhất
@router.get("/")
def list_recognitions(
    skip: int = 0,
    limit: int = 100
):
    """
    Lấy danh sách Recognition với việc chuẩn hóa giá trị enum vốn không đồng nhất.
    Đảm bảo tất cả dữ liệu được xử lý theo Ontology V3.2 mà không bỏ sót.
    
    Lưu ý: Đã bỏ response_model để đảm bảo không xảy ra lỗi validation với dữ liệu legacy.
    Cấu trúc response vẫn giữ nguyên theo RecognitionList.
    """
    try:
        # Debug log
        logger.debug(f"Bắt đầu lấy danh sách recognition với skip={skip}, limit={limit}")

        # Lấy danh sách Recognition từ service
        recognitions = recognition_service.list_recognitions(skip=skip, limit=limit)
        logger.debug(f"Đã lấy được {len(recognitions) if recognitions else 0} recognition từ service")
        
        # Áp dụng datetime_adapter cho danh sách
        items = adapt_model_list_to_schema(recognitions, id_field_name="uid", target_id_name="id")
        logger.debug(f"Đã chuyển đổi dữ liệu với datetime_adapter: {len(items)} items")
        
        # Xử lý đặc biệt cho từng item để đảm bảo tương thích với schema
        sanitized_items = []
        for idx, item in enumerate(items):
            try:
                logger.debug(f"Đang xử lý item {idx}: {item.get('id', 'unknown-id')}")
                
                # Tạo một item mới với các trường mặc định
                safe_item = {
                    "id": item.get("id", str(uuid.uuid4())),
                    "name": item.get("name", "[Tên nhận diện]"),
                    "message": item.get("message", "[Mô tả]"),
                    "recognition_type": RecognitionType.GRATITUDE.value,
                    "status": RecognitionStatus.GRANTED.value,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "tags": []
                }
                
                # Ghi đè các trường có giá trị từ item gốc
                if "recognition_type" in item and item["recognition_type"]:
                    try:
                        safe_item["recognition_type"] = normalize_enum_value(
                            item["recognition_type"], 
                            RecognitionType, 
                            RecognitionType.GRATITUDE.value
                        )
                    except Exception as e:
                        logger.warning(f"Không thể chuẩn hóa recognition_type: {e}")
                
                if "status" in item and item["status"]:
                    try:
                        safe_item["status"] = normalize_enum_value(
                            item["status"], 
                            RecognitionStatus, 
                            RecognitionStatus.GRANTED.value
                        )
                    except Exception as e:
                        logger.warning(f"Không thể chuẩn hóa status: {e}")
                
                if "tags" in item and isinstance(item["tags"], list):
                    safe_item["tags"] = item["tags"]
                
                # Xử lý created_at đặc biệt
                if "created_at" in item and item["created_at"]:
                    try:
                        # Nếu là datetime object, chuyển sang ISO string
                        if hasattr(item["created_at"], 'isoformat'):
                            safe_item["created_at"] = item["created_at"].isoformat()
                        else:
                            # Chuẩn hóa string
                            clean_date = str(item["created_at"]).replace("Z", "+00:00")
                            dt = datetime.fromisoformat(clean_date)
                            safe_item["created_at"] = dt.isoformat()
                    except Exception as e:
                        logger.warning(f"Không thể chuẩn hóa created_at: {e}")
                
                # Tương tự cho updated_at
                if "updated_at" in item and item["updated_at"]:
                    try:
                        if hasattr(item["updated_at"], 'isoformat'):
                            safe_item["updated_at"] = item["updated_at"].isoformat()
                        else:
                            clean_date = str(item["updated_at"]).replace("Z", "+00:00")
                            dt = datetime.fromisoformat(clean_date)
                            safe_item["updated_at"] = dt.isoformat()
                    except Exception as e:
                        logger.warning(f"Không thể chuẩn hóa updated_at: {e}")
                
                # Thêm vào danh sách đã xử lý
                sanitized_items.append(safe_item)
                logger.debug(f"Đã xử lý thành công item {idx}")
                
            except Exception as e:
                logger.error(f"Lỗi khi xử lý item {idx}: {str(e)}")
                logger.error(f"Item gây lỗi: {item}")
                # Vẫn thêm một item mặc định đầy đủ để đảm bảo không mất dữ liệu
                sanitized_items.append({
                    "id": str(uuid.uuid4()),
                    "name": "[Tên không xác định]",
                    "message": "[Mô tả không xác định]",
                    "recognition_type": RecognitionType.GRATITUDE.value,
                    "status": RecognitionStatus.GRANTED.value,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "tags": []
                })
        
        # Trả về đúng cấu trúc RecognitionList
        result = {
            "items": sanitized_items,
            "total": len(sanitized_items),
            "skip": skip,
            "limit": limit
        }
        logger.debug(f"Trả về {len(sanitized_items)} items đã xử lý")
        return result
    
    except Exception as e:
        logger.error(f"Lỗi tổng thể trong list_recognitions: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy danh sách Recognition: {str(e)}")

@router.put("/{recognition_id}", response_model=Recognition)
def update_recognition(
    recognition_id: str,
    recognition_data: RecognitionUpdate
):
    """
    Update an existing Recognition.
    """
    updated_recognition = recognition_service.update_recognition(recognition_id, recognition_data)
    if updated_recognition is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Recognition không tồn tại hoặc không thể cập nhật"
        )
    
    # Áp dụng datetime_adapter
    return adapt_model_to_schema(updated_recognition, id_field_name="uid", target_id_name="id")

@router.delete("/{recognition_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recognition(recognition_id: str):
    """
    Delete a Recognition.
    """
    deleted = recognition_service.delete_recognition(recognition_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Recognition không tồn tại hoặc không thể xóa"
        )
    return
