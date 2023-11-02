from fastapi import FastAPI
from api.endpoints import user, payment, workspace, content

app = FastAPI()

API_PREFIX = "/api"

app.include_router(user.router,tags=["User"], prefix=API_PREFIX)
app.include_router(payment.router,tags=["Payment"], prefix=API_PREFIX)
app.include_router(workspace.router,tags=["Workspace"], prefix=API_PREFIX)
app.include_router(content.router,tags=["Content"], prefix=API_PREFIX)
