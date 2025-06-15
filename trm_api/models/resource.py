from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid
from enum import Enum


class ResourceType(str, Enum):
    """Enum for all possible resource types in the ontology."""
    FINANCIAL = "Financial"
    KNOWLEDGE = "Knowledge"
    HUMAN = "Human"
    TOOL = "Tool"
    EQUIPMENT = "Equipment"
    SPACE = "Space"


class ResourceBase(BaseModel):
    """Base model for all resources with common fields."""
    name: str = Field(..., min_length=3, max_length=100, description="The name of the resource.")
    description: Optional[str] = Field(None, max_length=1000, description="A detailed description of the resource.")
    resource_type: ResourceType = Field(..., alias="resourceType", description="The type of resource.")
    status: str = Field("available", description="The current status of the resource (e.g., available, in_use, depleted).")
    owner_agent_id: Optional[str] = Field(None, alias="ownerAgentId", description="The ID of the agent who owns this resource.")
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "name": "Development Server Cluster",
                "description": "High-performance computing cluster for development and testing.",
                "resourceType": "Equipment",
                "status": "available",
                "ownerAgentId": "agent_123"
            }
        }
    )


# Financial Resource
class FinancialResourceDetails(BaseModel):
    """Specific details for a financial resource."""
    amount: float = Field(..., description="The amount of financial resource.")
    currency: str = Field("USD", description="The currency of the financial amount.")
    budget_code: Optional[str] = Field(None, alias="budgetCode", description="Budget code for accounting purposes.")
    allocation_date: Optional[datetime] = Field(None, alias="allocationDate", description="When this financial resource was allocated.")
    expiry_date: Optional[datetime] = Field(None, alias="expiryDate", description="When this financial resource expires if applicable.")


class FinancialResourceCreate(ResourceBase):
    """Create model for a financial resource."""
    resource_type: ResourceType = Field(ResourceType.FINANCIAL, alias="resourceType")
    details: FinancialResourceDetails


class FinancialResourceUpdate(BaseModel):
    """Update model for a financial resource."""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None)
    owner_agent_id: Optional[str] = Field(None, alias="ownerAgentId")
    details: Optional[FinancialResourceDetails] = Field(None)


# Knowledge Resource
class KnowledgeResourceDetails(BaseModel):
    """Specific details for a knowledge resource."""
    format: str = Field(..., description="The format of the knowledge resource (e.g., document, video, database).")
    location: str = Field(..., description="Where the knowledge resource is stored (URL, file path, etc.).")
    access_level: str = Field("public", alias="accessLevel", description="Who can access this resource (public, team, private).")
    tags: Optional[List[str]] = Field(None, description="Tags to categorize the knowledge resource.")
    created_by: Optional[str] = Field(None, alias="createdBy", description="ID of the agent who created this knowledge resource.")


class KnowledgeResourceCreate(ResourceBase):
    """Create model for a knowledge resource."""
    resource_type: ResourceType = Field(ResourceType.KNOWLEDGE, alias="resourceType")
    details: KnowledgeResourceDetails


class KnowledgeResourceUpdate(BaseModel):
    """Update model for a knowledge resource."""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None)
    owner_agent_id: Optional[str] = Field(None, alias="ownerAgentId")
    details: Optional[KnowledgeResourceDetails] = Field(None)


# Human Resource
class HumanResourceDetails(BaseModel):
    """Specific details for a human resource."""
    user_id: str = Field(..., alias="userId", description="ID of the user representing this human resource.")
    role: str = Field(..., description="Role of this human resource (e.g., developer, designer, manager).")
    availability: str = Field("full-time", description="Availability of this human resource (e.g., full-time, part-time).")
    allocation_percentage: Optional[float] = Field(None, alias="allocationPercentage", description="Percentage of time allocated to this resource.")
    skills: Optional[List[str]] = Field(None, description="IDs of skills possessed by this human resource.")


class HumanResourceCreate(ResourceBase):
    """Create model for a human resource."""
    resource_type: ResourceType = Field(ResourceType.HUMAN, alias="resourceType")
    details: HumanResourceDetails


class HumanResourceUpdate(BaseModel):
    """Update model for a human resource."""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None)
    owner_agent_id: Optional[str] = Field(None, alias="ownerAgentId")
    details: Optional[HumanResourceDetails] = Field(None)


# Tool Resource
class ToolResourceDetails(BaseModel):
    """Specific details for a tool resource."""
    tool_id: Optional[str] = Field(None, alias="toolId", description="ID of the tool in the system if it exists.")
    type: str = Field(..., description="Type of the tool (e.g., software, hardware, SaaS).")
    version: Optional[str] = Field(None, description="Version of the tool.")
    license_info: Optional[str] = Field(None, alias="licenseInfo", description="License information for the tool.")
    access_url: Optional[str] = Field(None, alias="accessUrl", description="URL to access the tool.")
    api_endpoint: Optional[str] = Field(None, alias="apiEndpoint", description="API endpoint for the tool.")


class ToolResourceCreate(ResourceBase):
    """Create model for a tool resource."""
    resource_type: ResourceType = Field(ResourceType.TOOL, alias="resourceType")
    details: ToolResourceDetails


class ToolResourceUpdate(BaseModel):
    """Update model for a tool resource."""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None)
    owner_agent_id: Optional[str] = Field(None, alias="ownerAgentId")
    details: Optional[ToolResourceDetails] = Field(None)


# Equipment Resource
class EquipmentResourceDetails(BaseModel):
    """Specific details for an equipment resource."""
    serial_number: Optional[str] = Field(None, alias="serialNumber", description="Serial number of the equipment.")
    model: Optional[str] = Field(None, description="Model of the equipment.")
    manufacturer: Optional[str] = Field(None, description="Manufacturer of the equipment.")
    purchase_date: Optional[datetime] = Field(None, alias="purchaseDate", description="When the equipment was purchased.")
    warranty_expiry: Optional[datetime] = Field(None, alias="warrantyExpiry", description="When the warranty expires.")
    location: Optional[str] = Field(None, description="Physical location of the equipment.")


class EquipmentResourceCreate(ResourceBase):
    """Create model for an equipment resource."""
    resource_type: ResourceType = Field(ResourceType.EQUIPMENT, alias="resourceType")
    details: EquipmentResourceDetails


class EquipmentResourceUpdate(BaseModel):
    """Update model for an equipment resource."""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None)
    owner_agent_id: Optional[str] = Field(None, alias="ownerAgentId")
    details: Optional[EquipmentResourceDetails] = Field(None)


# Space Resource
class SpaceResourceDetails(BaseModel):
    """Specific details for a space resource."""
    location: str = Field(..., description="Physical location of the space.")
    capacity: Optional[int] = Field(None, description="Maximum capacity of the space.")
    facilities: Optional[List[str]] = Field(None, description="Available facilities in the space.")
    booking_required: bool = Field(True, alias="bookingRequired", description="Whether booking is required to use this space.")
    booking_url: Optional[str] = Field(None, alias="bookingUrl", description="URL to book the space.")
    available_from: Optional[datetime] = Field(None, alias="availableFrom", description="When the space becomes available.")
    available_to: Optional[datetime] = Field(None, alias="availableTo", description="When the space becomes unavailable.")


class SpaceResourceCreate(ResourceBase):
    """Create model for a space resource."""
    resource_type: ResourceType = Field(ResourceType.SPACE, alias="resourceType")
    details: SpaceResourceDetails


class SpaceResourceUpdate(BaseModel):
    """Update model for a space resource."""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None)
    owner_agent_id: Optional[str] = Field(None, alias="ownerAgentId")
    details: Optional[SpaceResourceDetails] = Field(None)


# Generic Resource Create/Update models
class ResourceCreate(ResourceBase):
    """Generic model for creating any type of resource."""
    details: dict = Field(..., description="Resource type-specific details stored as a JSON dictionary.")


class ResourceUpdate(BaseModel):
    """Generic model for updating any type of resource."""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None)
    owner_agent_id: Optional[str] = Field(None, alias="ownerAgentId")
    details: Optional[dict] = Field(None, description="Resource type-specific details stored as a JSON dictionary.")


# Base Resource models for DB and API
class ResourceInDB(ResourceBase):
    """Base model for all resources as stored in the database."""
    uid: str = Field(..., description="Unique identifier of the resource.")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    details: dict = Field(..., description="Resource type-specific details stored as a JSON dictionary.")


class Resource(ResourceInDB):
    """Model for all resources as returned by the API."""
    pass
