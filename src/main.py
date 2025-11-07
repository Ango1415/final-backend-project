import uvicorn
from src.app.app import app
from src.app.routes import user_routes, project_routes, document_routes


"""
TODO:
    - Add logger functionality.
    - Complete some integration test cases for routes functionality    
"""

if __name__ == "__main__":
    print("hello world")
    uvicorn.run(app, host="0.0.0.0", port=8000)
