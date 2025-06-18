from neomodel import StructuredRel, StringProperty, DateTimeProperty, IntegerProperty
from datetime import datetime

class AssignedToProjectRel(StructuredRel):
    """
    Relationship representing a Resource being assigned to a Project.
    
    This relationship captures details about how a Resource is allocated to a Project,
    including allocation percentage, assignment period, and allocation context.
    """
    allocation_percentage = IntegerProperty(default=100,
                                          help_text="Percentage of resource allocated to this project (0-100)")
    
    assigned_at = DateTimeProperty(default=datetime.now,
                                 help_text="When the resource was assigned to this project")
    
    expected_end_date = DateTimeProperty(help_text="When the resource allocation is expected to end")
    
    actual_end_date = DateTimeProperty(help_text="When the resource allocation actually ended")
    
    assignment_type = StringProperty(default="full",
                                   help_text="Type of assignment (full, partial, on-demand)")
    
    assignment_status = StringProperty(default="active",
                                     help_text="Status of the assignment (active, completed, on-hold, cancelled)")
    
    notes = StringProperty(help_text="Notes about this resource assignment")
    
    assigned_by = StringProperty(help_text="UID of the Agent who assigned this resource")
    
    def __str__(self):
        return f"AssignedToProject({self.allocation_percentage}%)"
