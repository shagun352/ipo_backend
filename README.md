# FastAPI IPO Backend

This is a backend service built with FastAPI for managing IPO-related information and performing operations such as fetching and updating IPO allotment statuses for specific PAN numbers.

## Features
- Fetch and update IPO details from external APIs.
- Maintain a database of PAN numbers and their IPO statuses.
- Support for rechecking invalid PAN statuses.
- Easy-to-use API endpoints.

## Prerequisites
- Python 3.9 or later
- A running database (e.g., PostgreSQL, MySQL, SQLite, etc.)
- Git for version control

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/fastapi-ipo-backend.git
   cd fastapi-ipo-backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   - Configure your database connection string in `alembic.ini` 
   - Initialize the database:
     ```bash
     alembic upgrade head
     ```

5. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload