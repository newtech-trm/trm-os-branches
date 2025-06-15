import requests
import json
from datetime import datetime, timezone
import sys

print("seed_event_data.py: Script execution started.", flush=True)

BASE_URL = "http://localhost:8002/api/v1"

# --- Helper Functions ---
def print_json(data, indent=4):
    print(json.dumps(data, indent=indent, default=str), flush=True)

def get_existing_agents():
    try:
        response = requests.get(f"{BASE_URL}/agents?limit=5")
        response.raise_for_status()
        agents = response.json()
        print(f"\n--- Found {len(agents)} Agents ---", flush=True)
        # print_json(agents)
        return agents
    except json.JSONDecodeError as e_json:
        print(f"Error decoding JSON from /agents: {e_json}", flush=True)
        # response_text = "<unavailable>"
        # if 'response' in locals() and hasattr(response, 'text'): # This check is unreliable here
        #     response_text = response.text
        # print(f"Problematic response content for /agents: {response_text}", flush=True)
        return []
    except requests.exceptions.RequestException as e_req:
        print(f"Error fetching agents: {e_req}", flush=True)
        if e_req.response is not None:
            print(f"Response status: {e_req.response.status_code}", flush=True)
            print(f"Response content for /agents: {e_req.response.text}", flush=True)
        return []
    except Exception as e_gen:
        print(f"An unexpected error occurred in get_existing_agents: {e_gen}", flush=True)
        return []

def get_existing_projects():
    try:
        response = requests.get(f"{BASE_URL}/projects?limit=5")
        response.raise_for_status()
        projects = response.json()
        print(f"\n--- Found {len(projects)} Projects ---", flush=True)
        # print_json(projects)
        return projects
    except json.JSONDecodeError as e_json:
        print(f"Error decoding JSON from /projects: {e_json}", flush=True)
        # response_text = "<unavailable>"
        # if 'response' in locals() and hasattr(response, 'text'): # This check is unreliable here
        #     response_text = response.text
        # print(f"Problematic response content for /projects: {response_text}", flush=True)
        return []
    except requests.exceptions.RequestException as e_req:
        print(f"Error fetching projects: {e_req}", flush=True)
        if e_req.response is not None:
            print(f"Response status: {e_req.response.status_code}", flush=True)
            print(f"Response content for /projects: {e_req.response.text}", flush=True)
        return []
    except Exception as e_gen:
        print(f"An unexpected error occurred in get_existing_projects: {e_gen}", flush=True)
        return []

# --- Main Seeding Logic ---
def seed_events():
    print("\n--- Starting Event Seeding ---", flush=True)

    agents = get_existing_agents()
    projects = get_existing_projects()

    if not agents:
        print("No agents found. Cannot seed events that require an actor.", flush=True)
        return

    if not projects:
        print("No projects found. Cannot seed events that require a project context.", flush=True)
        return

    # Select the first agent as actor and first project as context for simplicity
    actor_agent = agents[0]
    context_project = projects[0]

    # Kiểm tra cả hai trường uid và agentId (API trả về agentId nhưng script cũ sử dụng uid)
    actor_uid = actor_agent.get('uid') or actor_agent.get('agentId')
    context_uid = context_project.get('uid') or context_project.get('projectId')
    
    if not actor_uid:
        print(f"Actor agent does not have a 'uid' hoặc 'agentId'. Agent data: {actor_agent}", flush=True)
        return
    if not context_uid:
        print(f"Context project does not have a 'uid' hoặc 'projectId'. Project data: {context_project}", flush=True)
        return

    print(f"Using Actor UID: {actor_uid} (Agent: {actor_agent.get('name')})", flush=True)
    print(f"Using Context UID: {context_uid} (Project: {context_project.get('name')})", flush=True)

    # TODO: Define event payloads and make POST requests
    event_payloads = []

    # Example Event 1: User login
    event_payloads.append({
        "name": "USER_LOGIN",  # Thêm trường name theo yêu cầu của schema
        "actor_uid": actor_uid,
        "context_uid": actor_uid, # Context can be the user themselves
        "context_node_label": "Agent",  # Sửa context_type thành context_node_label theo schema
        "payload": {"ip_address": "192.168.1.100", "login_method": "password"},  # Sửa data thành payload theo schema
        "description": f"{actor_agent.get('name', 'User')} logged in.",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    # Example Event 2: Project update by founder
    event_payloads.append({
        "name": "PROJECT_STATUS_UPDATED",  # Thêm trường name theo yêu cầu của schema
        "actor_uid": actor_uid, # Assuming the first agent is the founder
        "context_uid": context_uid,
        "context_node_label": "Project",  # Sửa context_type thành context_node_label theo schema
        "payload": {"old_status": "planning", "new_status": "in_progress", "updated_by": actor_agent.get('name')},  # Sửa data thành payload theo schema
        "description": f"Project '{context_project.get('name')}' status updated to 'in_progress' by {actor_agent.get('name')}.",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    # Example Event 3: Task assigned within project
    # For this, we'd ideally need a task_uid. For now, let's use project_uid as context.
    event_payloads.append({
        "name": "TASK_ASSIGNED",  # Thêm trường name theo yêu cầu của schema
        "actor_uid": actor_uid, # Assigner
        "context_uid": context_uid, # Project context
        "context_node_label": "Project",  # Sửa context_type thành context_node_label theo schema
        "payload": {"task_name": "Develop API endpoint", "assignee_name": "Dev Team Member", "due_date": "2024-12-31"},  # Sửa data thành payload theo schema
        "description": f"Task 'Develop API endpoint' assigned in project '{context_project.get('name')}'.",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    created_events_count = 0
    for i, payload in enumerate(event_payloads):
        print(f"\n--- Creating Event {i+1} ---", flush=True)
        print_json(payload)
        try:
            response = requests.post(f"{BASE_URL}/events/", json=payload)
            response.raise_for_status() # Raise an exception for bad status codes
            created_event = response.json()
            print("Event created successfully:", flush=True)
            print_json(created_event)
            created_events_count += 1
        except json.JSONDecodeError as e_json_post:
            print(f"Error decoding JSON from POST /events/ response: {e_json_post}", flush=True)
            if 'response' in locals() and hasattr(response, 'text'):
                 print(f"Problematic POST /events/ response content: {response.text}", flush=True)
        except requests.exceptions.HTTPError as e_http:
            print(f"HTTP error creating event: {e_http.response.status_code} - {e_http.response.reason}", flush=True)
            print(f"Response content from POST /events/: {e_http.response.text}", flush=True)
        except requests.exceptions.RequestException as e_req_post:
            print(f"Error creating event (RequestException): {e_req_post}", flush=True)
        except Exception as e_gen_post:
            print(f"An unexpected error occurred during event creation: {e_gen_post}", flush=True)

    print(f"\n--- Event Seeding Finished: {created_events_count}/{len(event_payloads)} events created successfully. ---", flush=True)

if __name__ == "__main__":
    seed_events()
    print("seed_event_data.py: Script execution finished.", flush=True)
