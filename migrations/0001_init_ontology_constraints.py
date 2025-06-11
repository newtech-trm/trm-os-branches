import os
import sys
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Add project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Load environment variables from .env file
load_dotenv(os.path.join(project_root, '.env'))

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

# --- Ontology Definitions ---
# This list defines the unique constraints for each node type (Label) in our ontology.
# Format: (LabelName, UniquePropertyName)
CONSTRAINTS_TO_CREATE = [
    ("Project", "projectId"),
    ("Tension", "tensionId"),
    ("Task", "taskId"),
    ("Agent", "agentId"),
    ("Event", "eventId"),
    ("Team", "teamId"),
    ("Tool", "toolId"),
    ("User", "userId"), # Note: Ontology doc refers to UserAccount, but model is User
    ("WIN", "winId"), # Note: Ontology doc refers to WIN, model is Win
    ("Recognition", "recognitionId"),
    ("KnowledgeSnippet", "snippetId"),
    ("Skill", "skillId"),
]

def create_constraints(driver):
    """Creates unique constraints on nodes in the Neo4j database."""
    print("Starting to create constraints...")
    with driver.session() as session:
        for label, prop in CONSTRAINTS_TO_CREATE:
            try:
                query = f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.{prop} IS UNIQUE"
                session.run(query)
                print(f"  [SUCCESS] Constraint created for Label='{label}', Property='{prop}'")
            except Exception as e:
                print(f"  [ERROR] Could not create constraint for Label='{label}', Property='{prop}'. Reason: {e}")
    print("Finished creating constraints.")

def main():
    """Main function to connect to Neo4j and run the migration."""
    if not all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD]):
        print("Error: Neo4j connection details are missing in the .env file.")
        return

    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        print("Successfully connected to Neo4j.")
        
        create_constraints(driver)
        
        driver.close()
        print("Connection to Neo4j closed.")
    except Exception as e:
        print(f"An error occurred while connecting to or interacting with Neo4j: {e}")

if __name__ == "__main__":
    main()
