from neo4j.time import DateTime
from neo4j.graph import Node

COMMON_ID_FIELDS = [
    "agentId", "resourceId", "projectId", "taskId", "eventId", 
    "winId", "recognitionId", "goalId", "objectiveId", "keyResultId", "metricId"
]

def to_py_native(obj):
    """
    Recursively converts Neo4j types (like DateTime) in a dictionary or list 
    to Python native types.
    """
    if isinstance(obj, dict):
        return {k: to_py_native(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_py_native(i) for i in obj]
    if isinstance(obj, DateTime):
        return obj.to_native()
    return obj

def process_record(record):
    """Converts a Neo4j Record into a dictionary, handling Node and DateTime objects."""
    if record is None:
        return None

    # Handles cases where the record is a single value (e.g., from RETURN u)
    if len(record.keys()) == 1:
        item = record.values()[0]
        if isinstance(item, Node):
            processed_node = {}
            id_field_found = None
            for node_key, node_value in item.items():
                if hasattr(node_value, 'to_native'): # Check for Neo4j temporal types
                    processed_node[node_key] = node_value.to_native()
                else:
                    processed_node[node_key] = node_value
                if node_key in COMMON_ID_FIELDS:
                    id_field_found = node_key
            
            if id_field_found:
                processed_node['uid'] = processed_node[id_field_found]
            return processed_node
        return item

    # Handles cases where the record has multiple fields
    processed_record = {}
    for key, value in record.items():
        if isinstance(value, Node):
            node_dict_for_key = {}
            id_field_found = None
            for node_prop_key, node_prop_value in value.items():
                if hasattr(node_prop_value, 'to_native'): # Check for Neo4j temporal types
                    node_dict_for_key[node_prop_key] = node_prop_value.to_native()
                else:
                    node_dict_for_key[node_prop_key] = node_prop_value
                if node_prop_key in COMMON_ID_FIELDS:
                    id_field_found = node_prop_key
            
            if id_field_found:
                node_dict_for_key['uid'] = node_dict_for_key[id_field_found]
            processed_record[key] = node_dict_for_key
        elif hasattr(value, 'to_native'):
            processed_record[key] = value.to_native()
        else:
            processed_record[key] = value
    return processed_record

def process_records(records):
    """
    Processes a list of Neo4j records.
    """
    return [process_record(record) for record in records]

def process_relationship_record(record):
    """
    Processes a Neo4j record representing a relationship, converting it to a dict.
    """
    if not record:
        return None
    
    record_as_dict = record.data() # .data() gives a dict view of the record
    return to_py_native(record_as_dict)
