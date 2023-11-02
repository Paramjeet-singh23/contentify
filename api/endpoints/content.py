from fastapi import FastAPI, Depends, HTTPException, APIRouter, UploadFile, File
from sqlalchemy.orm import Session
from db import crud, models, schemas
from db.database import SessionLocal, engine, get_db
from utils import auth
from typing import List
import os
from fastapi import UploadFile, Form
from fastapi.param_functions import File
import aiofiles
from core.config import MEDIA_PATH
import datetime

SUPPORTED_EXTENSIONS = ["mp4", "mov", "avi", "wmv", "flv", "webm", "mpeg4", "3gpp", "mpegps", "cineform", "hevc", "dnxhr", "prores"]




router = APIRouter()

# Content Endpoints
def is_owner_of_workspace(db: Session, user_id: int, workspace_id: int) -> bool:
    """Check if the user is the owner of the given workspace."""
    workspace = db.query(models.Workspace).filter(models.Workspace.id == workspace_id).first()
    if workspace and workspace.owner_id == user_id:
        return True
    return False

def verify_content_access(db: Session, user_id: int, content_id: int):
    """Verify if the user has access to the given content (either as an owner or workspace owner)."""
    content = crud.get_content(db, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    if content.user_id != user_id and not is_owner_of_workspace(db, user_id, content.workspace_id):
        raise HTTPException(status_code=403, detail="Access forbidden: You don't have permissions")

def verify_workspace_access(db: Session, user_id: int, workspace_id: int):
    """Verify if the user is a member or an owner of the given workspace."""
    # Check if the user is the owner
    if is_owner_of_workspace(db, user_id, workspace_id):
        return True
    
    # Check if the user is a member (you'll need a method to fetch this from your database)
    user_mapping = db.query(models.WorkspaceUserMapping).filter_by(workspace_id=workspace_id, user_id=user_id).first()
    
    if not user_mapping:
        raise HTTPException(status_code=403, detail="Access forbidden: You are not a member or owner of this workspace")
    
    return True


@router.post("/content/", response_model=schemas.Content)
async def create_content_endpoint(
    content: schemas.CreateContent,
    file: UploadFile = File(...),
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new content."""

    # Check if the file's extension is in the list of supported extensions
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    # Create a path to save the video, you can adjust this as needed
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    # Add the timestamp to the filename
    new_filename = f"{timestamp}_{file.filename}"

    file_path = os.path.join(MEDIA_PATH, new_filename)  
    file_path = os.path.join(MEDIA_PATH, file.filename)

    # Save the file in chunks
    async with aiofiles.open(file_path, 'wb') as buffer:
        while content := await file.read(1024):  # read by 1KB chunks
            await buffer.write(content)

    # Here, you could modify content.path to point to the saved file path if needed
    content.path = file_path

    # Then save the content metadata to the database
    return crud.create_content(db=db, content=content, user_id=current_user.id, workspace_id=content.workspace_id)

@router.get("/content/{content_id}", response_model=schemas.Content)
def get_content_by_id(content_id: int, current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Retrieve a content by its ID."""
    verify_content_access(db, current_user.id, content_id)
    db_content = crud.get_content(db, content_id=content_id)
    if not db_content:
        raise HTTPException(status_code=404, detail="Content not found")
    return db_content

@router.get("/contents/workspace/{workspace_id}", response_model=List[schemas.Content])
def get_contents_by_workspace_id(workspace_id: int, current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Retrieve all content items for a specific workspace."""
    verify_workspace_access(db, current_user.id, workspace_id)
    return crud.get_contents_by_workspace(db, workspace_id=workspace_id)


@router.get("/contents/user/", response_model=List[schemas.Content])
def get_contents_by_current_user(current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Retrieve all content items added by the currently authenticated user."""
    return crud.get_contents_by_user(db, user_id=current_user.id)

@router.put("/content/{content_id}", response_model=schemas.Content)
def update_content_endpoint(content_id: int, updated_content: schemas.UpdateContent, current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Update a content by its ID."""
    verify_content_access(db, current_user.id, content_id)
    db_content = crud.update_content(db, content_id=content_id, updated_content=updated_content)
    if not db_content:
        raise HTTPException(status_code=404, detail="Content not found")
    return db_content

@router.delete("/content/{content_id}", response_model=schemas.Content)
def delete_content_endpoint(content_id: int, current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Mark content as unavailable and delete its associated media."""
    verify_content_access(db, current_user.id, content_id)
    crud.delete_content(db, content_id=content_id)
    return {"status": "success", "message": "Content marked as unavailable and media deleted."}