"""
Unit tests for the FastAPI backend.

Tests all CRUD operations, filtering, sorting, and edge cases.
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.app import app
from database.init_db import init_database

# Test database path
TEST_DB = "data/test_projects.db"


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """Setup test database before tests, cleanup after."""
    # Remove existing test database
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    # Initialize test database
    init_database(TEST_DB)

    # Override database path in db_utils
    import database.db_utils as db_utils
    db_utils.DEFAULT_DB_PATH = TEST_DB

    yield

    # Cleanup
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_project():
    """Sample project data for testing."""
    return {
        "project_name": "Test Project",
        "description": "Test description",
        "industry": "Technology",
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
        "tools_used": "Python, FastAPI, SQLite",
        "role": "Developer",
        "client_organization": "TestCorp",
        "client_description": "Test client"
    }


def test_root_endpoint(client):
    """Test root endpoint returns API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "version" in data


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "unhealthy"]
    assert "database" in data


def test_create_project(client, sample_project):
    """Test creating a new project."""
    response = client.post("/api/projects", json=sample_project)
    assert response.status_code == 201
    data = response.json()

    # Check all fields
    assert data["project_name"] == sample_project["project_name"]
    assert data["description"] == sample_project["description"]
    assert data["industry"] == sample_project["industry"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_project_minimal(client):
    """Test creating project with only required fields."""
    minimal_project = {
        "project_name": "Minimal Project",
        "description": "Minimal description"
    }
    response = client.post("/api/projects", json=minimal_project)
    assert response.status_code == 201
    data = response.json()
    assert data["project_name"] == minimal_project["project_name"]
    assert data["industry"] is None
    assert data["start_date"] is None


def test_create_project_invalid_data(client):
    """Test creating project with invalid data."""
    # Missing required field
    invalid_project = {
        "description": "Missing project name"
    }
    response = client.post("/api/projects", json=invalid_project)
    assert response.status_code == 422  # Validation error

    # Empty required field
    invalid_project = {
        "project_name": "",
        "description": "Empty name"
    }
    response = client.post("/api/projects", json=invalid_project)
    assert response.status_code == 422


def test_create_project_invalid_dates(client):
    """Test creating project with end_date before start_date."""
    invalid_project = {
        "project_name": "Invalid Dates",
        "description": "End before start",
        "start_date": "2024-06-30",
        "end_date": "2024-01-01"
    }
    response = client.post("/api/projects", json=invalid_project)
    assert response.status_code == 422


def test_list_projects_empty(client):
    """Test listing projects when database is empty."""
    # Clear database by testing right after setup
    response = client.get("/api/projects")
    assert response.status_code == 200
    # Note: May have projects from previous tests, so just check it's a list
    assert isinstance(response.json(), list)


def test_list_projects(client, sample_project):
    """Test listing all projects."""
    # Create a few projects
    client.post("/api/projects", json=sample_project)
    client.post("/api/projects", json={
        "project_name": "Another Project",
        "description": "Another description",
        "industry": "Healthcare"
    })

    response = client.get("/api/projects")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_list_projects_with_filters(client, sample_project):
    """Test filtering projects."""
    # Create projects with different industries
    client.post("/api/projects", json={
        **sample_project,
        "project_name": "Energy Project",
        "industry": "Energy"
    })
    client.post("/api/projects", json={
        **sample_project,
        "project_name": "Tech Project",
        "industry": "Technology"
    })

    # Filter by industry
    response = client.get("/api/projects?industry=Energy")
    assert response.status_code == 200
    data = response.json()
    assert all(p["industry"] == "Energy" for p in data)


def test_list_projects_with_sorting(client, sample_project):
    """Test sorting projects."""
    # Create projects
    for i in range(3):
        client.post("/api/projects", json={
            **sample_project,
            "project_name": f"Project {i}"
        })

    # Sort by name ascending
    response = client.get("/api/projects?sort_by=project_name&order=asc")
    assert response.status_code == 200
    data = response.json()
    names = [p["project_name"] for p in data]
    assert names == sorted(names)

    # Sort by name descending
    response = client.get("/api/projects?sort_by=project_name&order=desc")
    assert response.status_code == 200
    data = response.json()
    names = [p["project_name"] for p in data]
    assert names == sorted(names, reverse=True)


def test_list_projects_invalid_sort(client):
    """Test invalid sort parameters."""
    # Invalid sort field (SQL injection attempt)
    response = client.get("/api/projects?sort_by=id;DROP+TABLE+work_projects")
    assert response.status_code == 400

    # Invalid order
    response = client.get("/api/projects?sort_by=project_name&order=invalid")
    assert response.status_code == 400


def test_get_project(client, sample_project):
    """Test getting a single project by ID."""
    # Create project
    create_response = client.post("/api/projects", json=sample_project)
    project_id = create_response.json()["id"]

    # Get project
    response = client.get(f"/api/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["project_name"] == sample_project["project_name"]


def test_get_project_not_found(client):
    """Test getting non-existent project."""
    response = client.get("/api/projects/99999")
    assert response.status_code == 404


def test_update_project(client, sample_project):
    """Test updating an existing project."""
    # Create project
    create_response = client.post("/api/projects", json=sample_project)
    project_id = create_response.json()["id"]

    # Update project
    update_data = {
        "project_name": "Updated Project",
        "industry": "Finance"
    }
    response = client.put(f"/api/projects/{project_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["project_name"] == update_data["project_name"]
    assert data["industry"] == update_data["industry"]
    # Check other fields unchanged
    assert data["description"] == sample_project["description"]


def test_update_project_empty(client, sample_project):
    """Test updating project with no fields (should return unchanged)."""
    # Create project
    create_response = client.post("/api/projects", json=sample_project)
    project_id = create_response.json()["id"]

    # Update with no fields
    response = client.put(f"/api/projects/{project_id}", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["project_name"] == sample_project["project_name"]


def test_update_project_not_found(client):
    """Test updating non-existent project."""
    response = client.put("/api/projects/99999", json={"project_name": "Updated"})
    assert response.status_code == 404


def test_delete_project(client, sample_project):
    """Test deleting a project."""
    # Create project
    create_response = client.post("/api/projects", json=sample_project)
    project_id = create_response.json()["id"]

    # Delete project
    response = client.delete(f"/api/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

    # Verify project deleted
    get_response = client.get(f"/api/projects/{project_id}")
    assert get_response.status_code == 404


def test_delete_project_not_found(client):
    """Test deleting non-existent project."""
    response = client.delete("/api/projects/99999")
    assert response.status_code == 404


def test_get_filter_options(client, sample_project):
    """Test getting filter options."""
    # Create projects with various values
    client.post("/api/projects", json={
        **sample_project,
        "industry": "Energy",
        "client_organization": "EnergyCorpA",
        "tools_used": "Python, Django"
    })
    client.post("/api/projects", json={
        **sample_project,
        "industry": "Technology",
        "client_organization": "TechCorpB",
        "tools_used": "JavaScript, React"
    })

    # Get filter options
    response = client.get("/api/projects/filters/options")
    assert response.status_code == 200
    data = response.json()

    assert "industries" in data
    assert "clients" in data
    assert "tools" in data

    assert isinstance(data["industries"], list)
    assert isinstance(data["clients"], list)
    assert isinstance(data["tools"], list)


def test_sql_injection_prevention(client):
    """Test that SQL injection attempts are prevented."""
    # Try SQL injection in project name
    malicious_project = {
        "project_name": "Test'; DROP TABLE work_projects; --",
        "description": "Malicious description"
    }
    response = client.post("/api/projects", json=malicious_project)
    # Should create project with the literal string (parameterized query prevents injection)
    assert response.status_code == 201

    # Verify table still exists by listing projects
    list_response = client.get("/api/projects")
    assert list_response.status_code == 200


def test_tools_filtering_partial_match(client, sample_project):
    """Test filtering by tools with partial match."""
    # Create project with specific tools
    client.post("/api/projects", json={
        **sample_project,
        "tools_used": "Python, FastAPI, SQLite"
    })

    # Filter by partial tool name
    response = client.get("/api/projects?tools=FastAPI")
    assert response.status_code == 200
    data = response.json()
    assert any("FastAPI" in p["tools_used"] for p in data if p["tools_used"])


def test_date_range_filtering(client, sample_project):
    """Test filtering by date range."""
    # Create projects with different dates
    client.post("/api/projects", json={
        **sample_project,
        "project_name": "Early Project",
        "start_date": "2023-01-01",
        "end_date": "2023-06-30"
    })
    client.post("/api/projects", json={
        **sample_project,
        "project_name": "Late Project",
        "start_date": "2024-07-01",
        "end_date": "2024-12-31"
    })

    # Filter by start_after
    response = client.get("/api/projects?start_after=2024-01-01")
    assert response.status_code == 200
    data = response.json()
    # Should only include projects starting in 2024 or later
    for project in data:
        if project["start_date"]:
            assert project["start_date"] >= "2024-01-01"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
