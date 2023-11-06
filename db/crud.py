from .models.user import User
from .models.workspace import Workspace, WorkspaceUserMapping
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .models.content import Content
from core.config import MEDIA_PATH
import os

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: User):
    hashed_password = bcrypt_context.hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        date_of_birth=user.date_of_birth
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_workspace(db: Session, workspace_id: int):
    return db.query(Workspace).filter(Workspace.id == workspace_id).first()


def get_workspaces_by_owner(db: Session, owner_id: int):
    return db.query(Workspace).filter(Workspace.owner_id == owner_id).all()


def create_workspace(db: Session, workspace: Workspace, owner_id: int):
    # Hash (or encrypt) the API key and secret
    hashed_api_key = bcrypt_context.hash(workspace.api_key)
    hashed_api_secret = bcrypt_context.hash(workspace.api_secret)

    # Create the Workspace entry
    db_workspace = Workspace(
        name=workspace.name,
        description=workspace.description,
        owner_id=owner_id,
        hashed_api_key=hashed_api_key,
        hashed_api_secret=hashed_api_secret
    )
    db.add(db_workspace)
    db.commit()
    db.refresh(db_workspace)

    # After the workspace has been created, add an entry to the WorkspaceUserMapping table designating the user as the owner
    workspace_user_mapping = WorkspaceUserMapping(
        workspace_id=db_workspace.id,
        user_id=owner_id,
        role='owner'
    )
    db.add(workspace_user_mapping)
    db.commit()
    db.refresh(workspace_user_mapping)

    return db_workspace


# Retrieve all user mappings for a specific workspace
def get_user_mappings_by_workspace(db: Session, workspace_id: int):
    return db.query(WorkspaceUserMapping).filter(WorkspaceUserMapping.workspace_id == workspace_id).all()

# Create a new user mapping for a workspace
def create_user_mapping_for_workspace(db: Session, workspace_id: int, user_id: int, role: str):
    mapping = WorkspaceUserMapping(
        workspace_id=workspace_id,
        user_id=user_id,
        role=role
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping


# 1. Create a new content item
def create_content(db: Session, content: Content, user_id: int):
    db_content = Content(
        name=content.name,
        title=content.title,
        path=content.path,
        user_id=user_id,
        workspace_id=content.workspace_id
    )
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content

# 2. Retrieve a content item by its ID
def get_content(db: Session, content_id: int):
    return db.query(Content).filter(Content.id == content_id).first()

# 3. Retrieve all content items for a given workspace
def get_contents_by_workspace(db: Session, workspace_id: int):
    return db.query(Content).filter(Content.workspace_id == workspace_id).all()

# 4. Retrieve all content items added by a given user
def get_contents_by_user(db: Session, user_id: int):
    return db.query(Content).filter(Content.user_id == user_id).all()

# 5. Update a content item by its ID
def update_content(db: Session, content_id: int, updated_content: Content):
    db_content = db.query(Content).filter(Content.id == content_id).first()
    if db_content:
        for key, value in updated_content.__dict__.items():
            setattr(db_content, key, value)
        db.commit()
        db.refresh(db_content)
    return db_content

def delete_content(db: Session, content_id: int):
    db_content = db.query(Content).filter(Content.id == content_id).first()
    if db_content:
        # Set is_available to False
        db_content.is_available = False
        
        # Delete the associated media file
        media_path = os.path.join(MEDIA_PATH, db_content.path)
        if os.path.exists(media_path):
            os.remove(media_path)

        # Save the changes to the database
        db.commit()