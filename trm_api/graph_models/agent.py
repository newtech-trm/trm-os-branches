from neomodel import StringProperty, RelationshipTo, BooleanProperty, DateTimeProperty, JSONProperty
from trm_api.graph_models.has_skill import HasSkillRel
from trm_api.graph_models.generates_event import GeneratesEventRel
from .base import BaseNode
import datetime

class Agent(BaseNode):
    """
    Represents an Agent in the TRM-OS ontology (Ontology v3.2).
    Agents can be human users (InternalAgent, ExternalAgent), AI systems (AIAgent, AGE),
    or other entities capable of performing actions in the TRM ecosystem.
    """
    # Core properties according to Ontology v3.2
    name = StringProperty(required=True, unique_index=True)
    # Agent type must be one of: InternalAgent, ExternalAgent, AIAgent, AGE
    agent_type = StringProperty(required=True, index=True, choices={
        'InternalAgent': 'Internal human agent (e.g., Founder, employee)',
        'ExternalAgent': 'External human agent (e.g., client, partner)',
        'AIAgent': 'Artificial Intelligence Agent',
        'AGE': 'Artificial Genesis Engine',
    })
    status = StringProperty(default='active', choices={
        'active': 'Agent is active and operational',
        'inactive': 'Agent is temporarily inactive',
        'error': 'Agent is in error state',
        'archived': 'Agent has been archived'
    })
    description = StringProperty()
    contact_info = JSONProperty()  # Optional contact information for human agents
    capabilities = JSONProperty()  # List of capabilities this agent possesses
    creation_date = DateTimeProperty(default=datetime.datetime.utcnow)
    last_modified_date = DateTimeProperty(default=datetime.datetime.utcnow)
    
    # Special properties for InternalAgent
    job_title = StringProperty()  # Only for InternalAgent
    department = StringProperty()  # Only for InternalAgent
    
    # Special properties for Founder (when agent_type is InternalAgent)
    is_founder = BooleanProperty(default=False)  # Identifies if this InternalAgent is a Founder
    founder_recognition_authority = BooleanProperty(default=False)  # If has authority to create Recognition

    # --- Relationships as defined in Ontology v3.2 ---
    # An agent can trigger events.
    triggered_events = RelationshipTo('Event', 'TRIGGERED_EVENT')

    # An agent can be managed by another agent (e.g., AGE).
    managed_by = RelationshipTo('Agent', 'MANAGED_BY')
    
    # An agent can manage other agents (especially for Founder and AGE) 
    manages = RelationshipTo('Agent', 'MANAGES')
    
    # An agent can have skills (with proficiency levels, etc.)
    has_skills = RelationshipTo('trm_api.graph_models.skill.GraphSkill', 'HAS_SKILL', model=HasSkillRel)
    
    # An agent can generate events
    # Use GeneratesEventRel to store relationship properties according to ontology V3.2
    generates_events = RelationshipTo('trm_api.graph_models.event.Event', 'GENERATES_EVENT', model=GeneratesEventRel)
    
    # Founder-specific relationships (when is_founder is True)
    recognizes = RelationshipTo('Resource', 'RECOGNIZES')  # Founder recognizes value in resources
    approves = RelationshipTo('Project', 'APPROVES')  # Founder approves projects
    guides = RelationshipTo('Agent', 'GUIDES')  # Founder guides other agents

    def __str__(self):
        if self.is_founder and self.agent_type == 'InternalAgent':
            return f"Founder: {self.name}"
        return f"{self.agent_type}: {self.name}"
        
    @property
    def is_internal_human(self):
        """Check if this agent is an internal human (employee or founder)"""
        return self.agent_type == 'InternalAgent'
        
    @property
    def is_ai_agent(self):
        """Check if this agent is an AI agent"""
        return self.agent_type in ['AIAgent', 'AGE']
    
    def has_founder_authority(self):
        """Check if this agent has Founder authority"""
        return self.is_founder and self.agent_type == 'InternalAgent'
