from fastapi import APIRouter

from trm_api.api.v1.endpoints import project, tension, task, user, team, skill #, win, recognition, knowledge_snippet, agent, event, tool

api_router = APIRouter()

# --- Active Routers ---
api_router.include_router(project.router, prefix="/projects", tags=["Projects"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(task.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(team.router, prefix="/teams", tags=["Teams"])
api_router.include_router(skill.router, prefix="/skills", tags=["Skills"])

# --- Deprecated Routers ---
api_router.include_router(tension.router, prefix="/tensions", tags=["Tensions"]) # Deprecated, will be removed

# --- TODO: Re-enable these routers after they are refactored to use repositories ---
# api_router.include_router(win.router, prefix="/wins", tags=["WINs"])
# api_router.include_router(recognition.router, prefix="/recognitions", tags=["Recognitions"])
# api_router.include_router(knowledge_snippet.router, prefix="/knowledge-snippets", tags=["Knowledge Snippets"])
# api_router.include_router(agent.router, prefix="/agents", tags=["Agents"])
# api_router.include_router(event.router, prefix="/events", tags=["Events"])
# api_router.include_router(tool.router, prefix="/tools", tags=["Tools"])
