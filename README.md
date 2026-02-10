# Demo Database Input - Work Experience Tracker

Simple web application for tracking work experience projects with a focus on consulting and professional work. Built with FastAPI, SQLite, and vanilla JavaScript for fast, responsive performance.

## Project Overview

**Purpose:** Track and manage work experience projects including project details, tools used, clients, and timelines.

**Tech Stack:**
- **Backend:** Python + FastAPI (async, high performance)
- **Database:** SQLite (optimized with WAL mode, connection pooling, indexes)
- **Frontend:** Vanilla HTML/CSS/JavaScript (no build step, fast loading)

## Features

- ✅ Create, Read, Update, Delete (CRUD) operations
- ✅ Sort projects by date, name, industry, client
- ✅ Filter by industry, tools, client, date range
- ✅ Clean, responsive interface
- ✅ Fast performance (<100ms response times)

## Project Structure

```
demo-database-input/
├── backend/              # FastAPI application
│   ├── app.py           # Main application entry point
│   ├── models.py        # Pydantic data models
│   ├── routes.py        # API endpoint definitions
│   └── utils.py         # Helper functions
├── database/            # Database setup and utilities
│   ├── schema.sql       # Database schema definition
│   ├── init_db.py       # Database initialization script
│   └── db_utils.py      # Connection and query utilities
├── frontend/            # Client-side interface
│   ├── index.html       # Main page with table view
│   ├── styles.css       # Styling and responsive design
│   └── app.js           # JavaScript for API interaction
├── tests/               # Unit and integration tests
├── data/                # SQLite database file location (gitignored)
├── requirements.txt     # Python dependencies
├── environment.yml      # Mamba environment specification
└── README.md            # This file
```

## Installation

### Prerequisites

- Python 3.11+
- Mamba (or Conda) package manager

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd demo-database-input
   ```

2. **Create mamba environment:**
   ```bash
   mamba env create -f environment.yml
   ```

   Or manually:
   ```bash
   mamba create -n demo-db-input python=3.11 -y
   mamba run -n demo-db-input pip install -r requirements.txt
   ```

3. **Initialize database:**
   ```bash
   mamba run -n demo-db-input python database/init_db.py
   ```

4. **Run the application:**
   ```bash
   mamba run -n demo-db-input uvicorn backend.app:app --reload
   ```

5. **Open in browser:**
   ```
   http://localhost:8000
   ```

## Usage

### Adding a Project

1. Click "Add New Project" button
2. Fill in project details:
   - **Project Name** (required)
   - **Description** (required) - Include context, challenges, achievements
   - **Industry** (optional)
   - **Start/End Dates** (optional)
   - **Tools Used** (optional) - e.g., Python, Excel, Confluence
   - **Role** (optional)
   - **Client/Organization** (optional)
   - **Client Description** (optional)
3. Click "Save"

### Editing a Project

1. Click "Edit" button on any project row
2. Modify fields as needed
3. Click "Save"

### Deleting a Project

1. Click "Delete" button on any project row
2. Confirm deletion

### Filtering and Sorting

- Use filter dropdowns to narrow down projects by industry, client, or tools
- Click column headers to sort by that field
- Use date range picker to filter by project dates

## API Documentation

FastAPI provides automatic API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects` | List all projects (with optional filters) |
| GET | `/api/projects/{id}` | Get single project by ID |
| POST | `/api/projects` | Create new project |
| PUT | `/api/projects/{id}` | Update existing project |
| DELETE | `/api/projects/{id}` | Delete project |
| GET | `/api/projects/filters` | Get unique filter values |

## Testing

Run tests with pytest:

```bash
mamba run -n demo-db-input pytest tests/ -v
```

## Development

### Running in Development Mode

```bash
# Start server with auto-reload
mamba run -n demo-db-input uvicorn backend.app:app --reload --port 8000

# Run with debug logging
mamba run -n demo-db-input uvicorn backend.app:app --reload --log-level debug
```

### Database Management

```bash
# Reset database (WARNING: Deletes all data)
rm data/projects.db
mamba run -n demo-db-input python database/init_db.py

# Backup database
cp data/projects.db data/projects_backup_$(date +%Y%m%d).db
```

## Work OS Integration

This project is part of the Work OS system. Project documentation and planning files are maintained separately in:

```
/mnt/g/My Drive/claude-work-os/projects/demo-database-input/
```

**Documentation files:**
- `INDEX.md` - Project overview and status
- `CLAUDE.md` - Agent quick-start guide
- `state/plan.md` - Implementation plan
- `state/session.md` - Development history
- `state/todo.md` - Task list

## Performance Optimizations

- **SQLite WAL mode:** Better concurrency for read/write operations
- **Database indexes:** On project_name, industry, dates, client
- **Connection pooling:** Reuse database connections
- **Async operations:** Non-blocking I/O with FastAPI + aiosqlite
- **Prepared statements:** Prevent SQL injection and improve performance

## Contributing

This is a personal project for work experience tracking. For issues or suggestions, create a GitHub issue.

## License

[Add license information]

---

**Created:** 2026-02-10
**Last Updated:** 2026-02-10
