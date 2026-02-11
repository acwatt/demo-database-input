"""
API routes for work projects CRUD operations.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from datetime import date
import logging

from .models import ProjectCreate, ProjectUpdate, ProjectResponse, FilterOptions
import sys
from pathlib import Path

# Add parent directory to path for database imports
sys.path.append(str(Path(__file__).parent.parent))
from database.db_utils import execute_query, fetch_one, fetch_all

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["projects"])


@router.post("/projects", response_model=ProjectResponse, status_code=201)
async def create_project(project: ProjectCreate):
    """
    Create a new work project.

    Args:
        project: Project data from request body

    Returns:
        Created project with ID and timestamps

    Raises:
        HTTPException: 400 if validation fails, 500 if database error
    """
    try:
        # Build INSERT query
        query = """
            INSERT INTO work_projects (
                project_name, description, industry, start_date, end_date,
                tools_used, role, client_organization, client_description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            project.project_name,
            project.description,
            project.industry,
            project.start_date,
            project.end_date,
            project.tools_used,
            project.role,
            project.client_organization,
            project.client_description
        )

        # Execute insert and get new ID
        new_id = await execute_query(query, params)

        # Fetch and return the created project
        created_project = await fetch_one(
            "SELECT * FROM work_projects WHERE id = ?",
            (new_id,)
        )

        if not created_project:
            raise HTTPException(status_code=500, detail="Failed to retrieve created project")

        return ProjectResponse(**created_project)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    industry: Optional[str] = Query(None, description="Filter by industry"),
    client: Optional[str] = Query(None, description="Filter by client organization"),
    tools: Optional[str] = Query(None, description="Filter by tools (partial match)"),
    start_after: Optional[date] = Query(None, description="Filter projects starting after date"),
    end_before: Optional[date] = Query(None, description="Filter projects ending before date"),
    sort_by: Optional[str] = Query("created_at", description="Sort by field"),
    order: Optional[str] = Query("desc", description="Sort order (asc/desc)")
):
    """
    List all work projects with optional filtering and sorting.

    Args:
        industry: Filter by exact industry match
        client: Filter by exact client organization match
        tools: Filter by partial tool name match
        start_after: Filter projects starting after this date
        end_before: Filter projects ending before this date
        sort_by: Field to sort by (default: created_at)
        order: Sort order - 'asc' or 'desc' (default: desc)

    Returns:
        List of projects matching filters

    Raises:
        HTTPException: 400 if invalid parameters, 500 if database error
    """
    try:
        # Validate sort_by field (prevent SQL injection)
        valid_sort_fields = [
            "id", "project_name", "industry", "start_date", "end_date",
            "client_organization", "created_at", "updated_at"
        ]
        if sort_by not in valid_sort_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort_by field. Must be one of: {', '.join(valid_sort_fields)}"
            )

        # Validate order
        if order.lower() not in ["asc", "desc"]:
            raise HTTPException(status_code=400, detail="Order must be 'asc' or 'desc'")

        # Build query with filters
        query = "SELECT * FROM work_projects WHERE 1=1"
        params = []

        if industry:
            query += " AND industry = ?"
            params.append(industry)

        if client:
            query += " AND client_organization = ?"
            params.append(client)

        if tools:
            query += " AND tools_used LIKE ?"
            params.append(f"%{tools}%")

        if start_after:
            query += " AND start_date >= ?"
            params.append(start_after)

        if end_before:
            query += " AND end_date <= ?"
            params.append(end_before)

        # Add sorting
        query += f" ORDER BY {sort_by} {order.upper()}"

        # Execute query
        projects = await fetch_all(query, tuple(params))

        return [ProjectResponse(**project) for project in projects]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int):
    """
    Get a single project by ID.

    Args:
        project_id: Project ID

    Returns:
        Project details

    Raises:
        HTTPException: 404 if not found, 500 if database error
    """
    try:
        project = await fetch_one(
            "SELECT * FROM work_projects WHERE id = ?",
            (project_id,)
        )

        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        return ProjectResponse(**project)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: int, project: ProjectUpdate):
    """
    Update an existing project.

    Args:
        project_id: Project ID to update
        project: Updated project data (all fields optional)

    Returns:
        Updated project details

    Raises:
        HTTPException: 404 if not found, 400 if validation fails, 500 if database error
    """
    try:
        # Check if project exists
        existing = await fetch_one(
            "SELECT * FROM work_projects WHERE id = ?",
            (project_id,)
        )

        if not existing:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        # Build UPDATE query with only provided fields
        updates = []
        params = []

        update_data = project.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            updates.append(f"{field} = ?")
            params.append(value)

        if not updates:
            # No fields to update, return existing project
            return ProjectResponse(**existing)

        # Add ID to params
        params.append(project_id)

        # Execute update
        query = f"UPDATE work_projects SET {', '.join(updates)} WHERE id = ?"
        await execute_query(query, tuple(params))

        # Fetch and return updated project
        updated_project = await fetch_one(
            "SELECT * FROM work_projects WHERE id = ?",
            (project_id,)
        )

        return ProjectResponse(**updated_project)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.delete("/projects/{project_id}")
async def delete_project(project_id: int):
    """
    Delete a project by ID.

    Args:
        project_id: Project ID to delete

    Returns:
        Success message

    Raises:
        HTTPException: 404 if not found, 500 if database error
    """
    try:
        # Check if project exists
        existing = await fetch_one(
            "SELECT * FROM work_projects WHERE id = ?",
            (project_id,)
        )

        if not existing:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

        # Delete project
        await execute_query(
            "DELETE FROM work_projects WHERE id = ?",
            (project_id,)
        )

        return {"message": f"Project {project_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/projects/filters/options", response_model=FilterOptions)
async def get_filter_options():
    """
    Get unique values for filter dropdowns.

    Returns:
        Available industries, clients, and tools for filtering

    Raises:
        HTTPException: 500 if database error
    """
    try:
        # Get unique industries
        industries_query = """
            SELECT DISTINCT industry FROM work_projects
            WHERE industry IS NOT NULL AND industry != ''
            ORDER BY industry
        """
        industries_data = await fetch_all(industries_query)
        industries = [row['industry'] for row in industries_data]

        # Get unique clients
        clients_query = """
            SELECT DISTINCT client_organization FROM work_projects
            WHERE client_organization IS NOT NULL AND client_organization != ''
            ORDER BY client_organization
        """
        clients_data = await fetch_all(clients_query)
        clients = [row['client_organization'] for row in clients_data]

        # Get unique tools (split by comma and deduplicate)
        tools_query = """
            SELECT DISTINCT tools_used FROM work_projects
            WHERE tools_used IS NOT NULL AND tools_used != ''
        """
        tools_data = await fetch_all(tools_query)
        tools_set = set()
        for row in tools_data:
            if row['tools_used']:
                # Split by comma and clean up
                for tool in row['tools_used'].split(','):
                    tool = tool.strip()
                    if tool:
                        tools_set.add(tool)
        tools = sorted(list(tools_set))

        return FilterOptions(
            industries=industries,
            clients=clients,
            tools=tools
        )

    except Exception as e:
        logger.error(f"Error fetching filter options: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
