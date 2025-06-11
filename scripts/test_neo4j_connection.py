import os
from dotenv import load_dotenv
from neo4j import GraphDatabase, exceptions

def test_connection():
    """
    A dedicated script to test the connection to Neo4j AuraDB with clear feedback.
    """
    # Load environment variables from .env file located in the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(dotenv_path=os.path.join(project_root, '.env'))

    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")

    print("--- Attempting to connect with the following credentials ---")
    print(f"URI: {uri}")
    print(f"User: {user}")
    
    # Mask password for security, showing only first and last characters
    if password:
        masked_password = f"{password[0]}...{password[-1]}" if len(password) > 1 else "*"
        print(f"Password: {masked_password} (Length: {len(password)})")
    else:
        print("Password: [NOT FOUND IN .env FILE]")
        return

    if not all([uri, user, password]):
        print("\nError: NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set in the .env file.")
        return

    driver = None
    try:
        print("\nAttempting to establish connection...")
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        print("\n=========================================================")
        print("SUCCESS: Connection to Neo4j AuraDB verified successfully!")
        print("=========================================================")
        print("This confirms your credentials and network access are correct.")

    except exceptions.AuthError as e:
        print("\n=========================================================")
        print("FAILURE: Authentication failed.")
        print("=========================================================")
        print("This means the username or password in your .env file is incorrect.")
        print("Please double-check for typos, extra spaces, or hidden characters.")
        print("As a final step, consider resetting the password in the Aura Console.")
        print(f"\nDriver Error Details: {e}")

    except exceptions.ServiceUnavailable as e:
        print("\n=========================================================")
        print(f"FAILURE: Could not connect to the server at {uri}.")
        print("=========================================================")
        print("This might be a network issue, a firewall, or an IP allowlist problem.")
        print("Please check the 'IP Allowlist' settings in your Aura Console.")
        print(f"\nDriver Error Details: {e}")

    except Exception as e:
        print(f"\nFAILURE: An unexpected error occurred: {e}")

    finally:
        if driver:
            driver.close()
            print("\nConnection closed.")

if __name__ == "__main__":
    test_connection()
