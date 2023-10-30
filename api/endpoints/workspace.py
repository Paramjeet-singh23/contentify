# Imports organized by package
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from db import crud, models, schemas
from db.database import SessionLocal, engine, get_db

from utils import auth
from typing import Annotated, List

# Instantiation
router = APIRouter()

# Workspace Endpoints

@router.post("/workspace/", response_model=schemas.Workspace)  # Ensure you have a schema named Workspace
def create_workspace_endpoint(workspace: schemas.CreateWorkspace, current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Create a new workspace."""
    return crud.create_workspace(db=db, workspace=workspace, owner_id=current_user.id)

@router.get("/workspace/{workspace_id}", response_model=schemas.Workspace)
def get_workspace_by_id(workspace_id: int, current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Retrieve a workspace by its ID."""
    db_workspace = crud.get_workspace(db, workspace_id=workspace_id)
    if not db_workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return db_workspace

@router.get("/workspaces/owner/{owner_id}", response_model=List[schemas.Workspace])  # Ensure you have a List imported from typing
def get_workspaces_by_owner_id(owner_id: int, current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Retrieve all workspaces by the owner's ID."""
    return crud.get_workspaces_by_owner(db, owner_id=owner_id)

# WorkspaceUserMapping Endpoints

@router.get("/workspace/{workspace_id}/users", response_model=List[schemas.WorkspaceUserMapping])  # Ensure you have a schema named WorkspaceUserMapping
def get_users_by_workspace_id(workspace_id: int, current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Retrieve all user mappings for a specific workspace."""
    return crud.get_user_mappings_by_workspace(db, workspace_id=workspace_id)

@router.post("/workspace/{workspace_id}/user", response_model=schemas.WorkspaceUserMapping)
def add_user_to_workspace(workspace_id: int, user_id: int, role: str, current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Add a user to a specific workspace with a designated role."""
    return crud.create_user_mapping_for_workspace(db, workspace_id=workspace_id, user_id=user_id, role=role)
