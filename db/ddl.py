import psycopg2

# Database connection parameters
dbname = "python_web"
user = "postgres"
password = "admin"
host = "localhost"

# Connect to an existing db
conn = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=password,
    host=host
)
cur = conn.cursor()

# SQL statements to create tables - DDL
create_users_table = """
    CREATE TABLE users (
        user_id SERIAL PRIMARY KEY NOT NULL,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    );
"""

create_projects_table = """
    CREATE TABLE projects (
        project_id SERIAL PRIMARY KEY NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        owner INTEGER NOT NULL,
        FOREIGN KEY(owner) REFERENCES users(user_id) ON DELETE CASCADE
    );
"""

create_project_participants_table = """
    CREATE TABLE project_participants (
        proj_part_id SERIAL PRIMARY KEY NOT NULL,
        user_id INTEGER NOT NULL,
        project_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE CASCADE
    );
"""

create_documents_table = """
    CREATE TABLE documents (
        document_id SERIAL PRIMARY KEY NOT NULL,
        attached_project INTEGER NOT NULL,
        name TEXT NOT NULL,
        format TEXT NOT NULL,
        file_url TEXT NOT NULL UNIQUE,
        FOREIGN KEY(attached_project) REFERENCES projects(project_id) ON DELETE CASCADE
    );
"""

if __name__ == '__main__':
    # Execute SQL commands to create tables
    try:
        cur.execute(create_users_table)
        cur.execute(create_projects_table)
        cur.execute(create_project_participants_table)
        cur.execute(create_documents_table)
        conn.commit()  # Commit changes to the db
        print("Tables created successfully")
    except Exception as e:
        print("Error occurred while creating tables:", e)
        conn.rollback()  # Rollback changes on error
    finally:
        cur.close()  # Close the cursor
        conn.close()  # Close the connection
