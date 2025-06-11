from neo4j import GraphDatabase, Driver
from trm_api.core.config import settings

# Singleton instance for the Neo4j driver
driver: Driver = None

def get_driver() -> Driver:
    """
    Returns the singleton Neo4j driver instance, creating it if necessary.
    """
    global driver
    if driver is None:
        print("Initializing Neo4j driver...")
        driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        # You can verify connectivity here if needed, but it's often done once at startup
        # driver.verify_connectivity()
    return driver

def close_driver():
    """
    Closes the Neo4j driver connection.
    """
    global driver
    if driver is not None:
        print("Closing Neo4j driver...")
        driver.close()
        driver = None

# We can also add event handlers to the main app to manage the driver lifecycle
# @app.on_event("startup")
# async def startup_event():
#     get_driver()

# @app.on_event("shutdown")
# async def shutdown_event():
#     close_driver()
