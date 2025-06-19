# TRM API Adapters Package
# Export các hàm và decorator để sử dụng trong toàn bộ dự án

# Datetime adapters
from .datetime_adapter import normalize_datetime, normalize_dict_datetimes

# Enum adapters
from .enum_adapter import (
    normalize_enum_value,
    normalize_win_status,
    normalize_win_type,
    normalize_recognition_type,
    normalize_recognition_status
)

# Decorator adapters
from .decorators import (
    adapt_response,
    adapt_datetime_response,
    adapt_win_response,
    adapt_recognition_response
)

# Version info
__version__ = '1.0.0'
