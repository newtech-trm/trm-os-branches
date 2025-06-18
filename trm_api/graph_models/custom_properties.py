"""
Custom property classes for neomodel to handle specific data types from Neo4j.
This file defines property types that are not available in neomodel's standard library.
"""

import datetime
import pytz
import neo4j.time
from neomodel.properties import Property
from neomodel.exceptions import InflateError, DeflateError
from neomodel import config

class Neo4jDateTimeProperty(Property):
    """
    A property that correctly handles neo4j.time.DateTime objects.
    
    This property allows smooth conversion between Python's datetime objects
    and Neo4j's DateTime objects, which neomodel's built-in DateTimeProperty
    cannot handle properly.
    
    :param default_now: If ``True``, the creation time (UTC) will be used as default.
                       Defaults to ``False``.
    :type default_now: :class:`bool`
    """
    form_field_class = "DateTimeField"

    def __init__(self, default_now=False, **kwargs):
        if default_now:
            if "default" in kwargs:
                raise ValueError("too many defaults")
            kwargs["default"] = lambda: datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        
        super().__init__(**kwargs)
    
    def inflate(self, value, node=None):
        """
        Convert neo4j.time.DateTime to Python datetime
        
        :param value: Value from the database (neo4j.time.DateTime)
        :param node: The node being inflated
        :return: Python datetime object with timezone
        """
        if value is None:
            return None
            
        try:
            # Case 1: Neo4j DateTime object
            if isinstance(value, neo4j.time.DateTime):
                # Create a Python datetime from Neo4j DateTime components
                dt = datetime.datetime(
                    year=value.year,
                    month=value.month,
                    day=value.day,
                    hour=value.hour,
                    minute=value.minute,
                    second=value.second,
                    microsecond=value.nanosecond // 1000,
                    tzinfo=pytz.utc
                )
                return dt
                
            # Case 2: Already a Python datetime
            elif isinstance(value, datetime.datetime):
                # Ensure timezone is set
                if value.tzinfo is None:
                    return value.replace(tzinfo=pytz.utc)
                return value
                
            # Case 3: Float timestamp (epoch)
            elif isinstance(value, (int, float)):
                return datetime.datetime.fromtimestamp(value, tz=pytz.UTC)
                
            # Case 4: String in ISO format
            elif isinstance(value, str):
                try:
                    dt = datetime.datetime.fromisoformat(value)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=pytz.utc)
                    return dt
                except ValueError:
                    # Try parsing common date formats
                    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                        try:
                            dt = datetime.datetime.strptime(value, fmt)
                            return dt.replace(tzinfo=pytz.utc)
                        except ValueError:
                            continue
                    raise InflateError(f"Cannot convert string '{value}' to datetime")
            
            raise InflateError(f"Cannot inflate {type(value)} to datetime")
            
        except Exception as e:
            raise InflateError(f"Failed to inflate {type(value)} to datetime: {str(e)}")
    
    def deflate(self, value, node=None):
        """
        Convert Python datetime to format suitable for Neo4j
        
        :param value: Python datetime object
        :param node: The node being deflated (optional)
        :return: Value suitable for Neo4j storage
        """
        if value is None:
            return None
            
        try:
            if isinstance(value, datetime.datetime):
                # Ensure timezone is set
                if value.tzinfo is None:
                    value = value.replace(tzinfo=pytz.utc)
                    
                # Neo4j driver handles Python datetime objects correctly
                return value
                
            elif isinstance(value, str):
                # Try to parse as ISO format
                try:
                    dt = datetime.datetime.fromisoformat(value)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=pytz.utc)
                    return dt
                except ValueError:
                    raise DeflateError(f"Cannot convert string '{value}' to datetime for Neo4j")
                    
            elif isinstance(value, (int, float)):
                # Convert timestamp to datetime
                return datetime.datetime.fromtimestamp(value, tz=pytz.UTC)
                
            raise DeflateError(f"Cannot deflate {type(value)} to Neo4j datetime")
            
        except Exception as e:
            raise DeflateError(f"Failed to deflate to Neo4j datetime: {str(e)}")
