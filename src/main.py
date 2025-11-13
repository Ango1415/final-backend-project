import uvicorn
from src.app.app import app
from src.app.routes import user_routes, project_routes, document_routes
from src.db.orm import inspect_tables_existence


"""
TODO:
    - Add logger functionality.
    - Complete some integration test cases for routes functionality    
"""

if __name__ == "__main__":
    inspect_tables_existence()
    print("Hello World")
    uvicorn.run(app, host="0.0.0.0", port=8000)
