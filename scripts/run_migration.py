import os
from dotenv import load_dotenv
from neo4j import GraphDatabase, exceptions

def run_migration():
    """
    Connects to the Neo4j AuraDB and runs the Cypher migration script.
    """
    # Load environment variables from .env file located in the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(dotenv_path=os.path.join(project_root, '.env'))

    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    migration_file_path = os.path.join(project_root, 'migrations', '001_init.cypher')

    if not all([uri, user, password]):
        print("Error: NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set in the .env file.")
        return

    driver = None
    try:
        # Establish a connection to the database
        print(f"Connecting to Neo4j at {uri}...")
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        print("Successfully connected to Neo4j AuraDB.")

        # Read the migration file
        with open(migration_file_path, 'r', encoding='utf-8') as f:
            cypher_script = f.read()

        # Split script into individual statements
        # Cypher statements are terminated by a semicolon
        statements = [stmt.strip() for stmt in cypher_script.split(';') if stmt.strip()]

        # Execute each statement
        with driver.session() as session:
            print(f"Found {len(statements)} statements to execute from {migration_file_path}...")
            for i, statement in enumerate(statements):
                if not statement:
                    continue
                try:
                    # Use write_transaction for schema operations to ensure they are atomic
                    session.execute_write(lambda tx: tx.run(statement))
                    print(f"  -> Successfully executed statement {i+1}/{len(statements)}: {statement[:100]}...")
                except exceptions.CypherSyntaxError as e:
                    print(f"  -> Syntax Error in statement: {statement}")
                    print(f"  -> {e}")
                    raise
                except Exception as e:
                    print(f"  -> An error occurred during execution of statement: {statement}")
                    print(f"  -> {e}")
                    raise
            
            print("\nMigration script executed successfully!")

    except exceptions.AuthError:
        print("Authentication failed. Please check your Neo4j credentials in the .env file.")
    except exceptions.ServiceUnavailable:
        print("Could not connect to Neo4j. Please check the URI and your network connection.")
    except FileNotFoundError:
        print(f"Error: Migration file not found at {migration_file_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure the driver is closed
        if driver:
            driver.close()
            print("Database connection closed.")

if __name__ == "__main__":
    run_migration()
