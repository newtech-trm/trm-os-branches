from typing import Any, Dict, Optional, List, Union
from datetime import datetime
from neo4j.time import DateTime as Neo4jDateTime


def convert_neo4j_datetime(dt_value: Union[Neo4jDateTime, datetime, None]) -> Optional[str]:
    """
    Convert Neo4j DateTime or Python datetime to ISO format string.
    
    Args:
        dt_value: Neo4j DateTime object, Python datetime object, or None
        
    Returns:
        ISO format string or None if input is None
    """
    if dt_value is None:
        return None
    
    # Handle both Neo4j DateTime and Python datetime
    if hasattr(dt_value, 'isoformat'):
        return dt_value.isoformat()
        
    # Fallback for any other datetime-like object
    return str(dt_value)


def adapt_datetime_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a dictionary and convert any datetime objects to ISO strings.
    
    Args:
        data: Dictionary potentially containing datetime objects
        
    Returns:
        Dictionary with datetime objects converted to ISO strings
    """
    result = {}
    
    for key, value in data.items():
        # Handle datetime objects
        if isinstance(value, (datetime, Neo4jDateTime)) or (
            hasattr(value, 'isoformat') and callable(getattr(value, 'isoformat'))
        ):
            result[key] = convert_neo4j_datetime(value)
        # Handle nested dictionaries
        elif isinstance(value, dict):
            result[key] = adapt_datetime_fields(value)
        # Handle lists that might contain datetime objects or dicts
        elif isinstance(value, list):
            result[key] = [
                adapt_datetime_fields(item) if isinstance(item, dict)
                else convert_neo4j_datetime(item) if isinstance(item, (datetime, Neo4jDateTime))
                else item
                for item in value
            ]
        else:
            result[key] = value
            
    return result


def adapt_model_to_schema(model: Any, id_field_name: str = "uid", target_id_name: str = "id") -> Dict[str, Any]:
    """
    Convert a Neo4j model to a dictionary compatible with Pydantic schema.
    This handles datetime conversions and ensures the ID field is properly named.
    
    Args:
        model: Neo4j model object
        id_field_name: The source field name to use as ID (default: "uid")
        target_id_name: The target field name for ID in response (default: "id")
        
    Returns:
        Dictionary with all datetime objects converted to ISO strings and standardized ID field
    """
    # Convert model to dict if it's not already
    if hasattr(model, '__dict__'):
        # Some models may have a to_dict() method
        if hasattr(model, 'to_dict') and callable(getattr(model, 'to_dict')):
            model_dict = model.to_dict()
        else:
            # Create a dictionary from the model's attributes
            model_dict = {k: v for k, v in model.__dict__.items() 
                         if not k.startswith('_') and not callable(v)}
    else:
        # Already a dict
        model_dict = model
        
    # Ensure the correct ID field is used
    if id_field_name in model_dict and target_id_name != id_field_name:
        model_dict[target_id_name] = model_dict.pop(id_field_name)
    
    # Process datetime fields
    result = adapt_datetime_fields(model_dict)
    
    # Filter out None values for optional fields
    return {k: v for k, v in result.items() if v is not None}


def adapt_model_list_to_schema(
    models: List[Any], 
    id_field_name: str = "uid", 
    target_id_name: str = "id"
) -> List[Dict[str, Any]]:
    """
    Convert a list of Neo4j models to a list of dictionaries compatible with Pydantic schema.
    
    Args:
        models: List of Neo4j model objects
        id_field_name: The source field name to use as ID
        target_id_name: The target field name for ID in response
        
    Returns:
        List of dictionaries with datetime objects converted to ISO strings and standardized ID field
    """
    return [adapt_model_to_schema(model, id_field_name, target_id_name) for model in models]
