import requests
import json
import random

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8000/api/v1"

# --- Helper Functions ---

def print_status(message, is_success=True):
    """Prints a formatted status message."""
    prefix = "✅ SUCCESS:" if is_success else "❌ ERROR:"
    print(f"{prefix} {message}")

def get_entities(entity_name):
    """Fetches all entities of a given type (e.g., 'users', 'tasks')."""
    try:
        response = requests.get(f"{BASE_URL}/{entity_name}/")
        response.raise_for_status()
        entities = response.json()
        if not entities:
            print_status(f"No entities found for '{entity_name}'. Cannot create relationships.", is_success=False)
            return []
        print_status(f"Successfully fetched {len(entities)} {entity_name}.")
        return entities
    except requests.exceptions.RequestException as e:
        print_status(f"Failed to fetch {entity_name}: {e}", is_success=False)
        return []

def create_relationship(endpoint_url):
    """Creates a relationship by sending a POST request."""
    try:
        response = requests.post(endpoint_url)
        response.raise_for_status()
        print_status(f"Created relationship via {endpoint_url}")
        return response.json()
    except requests.exceptions.RequestException as e:
        error_content = e.response.json() if e.response and e.response.headers.get('content-type') == 'application/json' else str(e)
        print_status(f"Failed to create relationship via {endpoint_url}. Details: {error_content}", is_success=False)
        return None

# --- Main Seeding Logic ---

def main():
    """Main function to seed relationships."""
    print("🚀 Starting relationship seeding process...")

    # 1. Fetch existing entities
    users = get_entities("users")
    tasks = get_entities("tasks")
    tensions = get_entities("tensions")
    projects = get_entities("projects")
    teams = get_entities("teams")

    if not all([users, tasks, tensions, projects, teams]):
        print_status("Halting seeding process due to missing entities.", is_success=False)
        return

    # 2. Create 'PERFORMS' relationships (User -> Task)
    print("\n🔗 Creating 'PERFORMS' relationships (assigning users to tasks)...")
    if tasks and users:
        for task in tasks:
            assignee = random.choice(users)
            url = f"{BASE_URL}/tasks/{task['task_id']}/assignee/{assignee['user_id']}"
            create_relationship(url)

    # 3. Create 'IDENTIFIED' relationships (User -> Tension)
    print("\n🔗 Creating 'IDENTIFIED' relationships (linking users to tensions)...")
    if tensions and users:
        for tension in tensions:
            identifier = random.choice(users)
            url = f"{BASE_URL}/tensions/{tension['tension_id']}/identifier/{identifier['user_id']}"
            create_relationship(url)

    # 4. Create 'HAS_MEMBER' relationships (Team -> User)
    print("\n🔗 Creating 'HAS_MEMBER' relationships (adding users to teams)...")
    if teams and users:
        for team in teams:
            members_to_add = random.sample(users, k=min(len(users), 2)) # Add up to 2 members
            for member in members_to_add:
                url = f"{BASE_URL}/teams/{team['team_id']}/member/{member['user_id']}"
                create_relationship(url)

    # 5. Create 'HAS_PARTICIPANT' relationships (Project -> User)
    print("\n🔗 Creating 'HAS_PARTICIPANT' relationships (adding users to projects)...")
    if projects and users:
        for project in projects:
            participants_to_add = random.sample(users, k=min(len(users), 3)) # Add up to 3 participants
            for participant in participants_to_add:
                url = f"{BASE_URL}/projects/{project['project_id']}/participant/{participant['user_id']}"
                create_relationship(url)

    print("\n🎉 Relationship seeding process completed.")


if __name__ == "__main__":
    main()
