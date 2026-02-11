-- Work Projects Database Schema
-- Created: 2026-02-10
-- Purpose: Track work experience projects (consulting/professional)

CREATE TABLE IF NOT EXISTS work_projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    description TEXT NOT NULL,
    industry TEXT,
    start_date DATE,
    end_date DATE,
    tools_used TEXT,
    role TEXT,
    client_organization TEXT,
    client_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance indexes for sorting and filtering
CREATE INDEX IF NOT EXISTS idx_project_name ON work_projects(project_name);
CREATE INDEX IF NOT EXISTS idx_industry ON work_projects(industry);
CREATE INDEX IF NOT EXISTS idx_start_date ON work_projects(start_date DESC);
CREATE INDEX IF NOT EXISTS idx_end_date ON work_projects(end_date DESC);
CREATE INDEX IF NOT EXISTS idx_client ON work_projects(client_organization);
CREATE INDEX IF NOT EXISTS idx_created_at ON work_projects(created_at DESC);

-- Auto-update trigger for updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_work_projects_timestamp
AFTER UPDATE ON work_projects
FOR EACH ROW
BEGIN
    UPDATE work_projects SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;
