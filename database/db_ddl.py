import psycopg2

# Database connection parameters
dbname = "python_web"
user = "postgres"
password = "admin"
host = "localhost"

# Connect to an existing database
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
        username TEXT NOT NULL,
        password TEXT NOT NULL
    );
"""

create_projects_table = """
    CREATE TABLE projects (
        project_id SERIAL PRIMARY KEY NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        owner INTEGER NOT NULL,
        FOREIGN KEY(owner) REFERENCES users(user_id)
    );
"""


# Execute SQL commands to create tables
try:
    cur.execute(create_users_table)
    cur.execute(create_projects_table)
    conn.commit()  # Commit changes to the database
    print("Tables created successfully")
except Exception as e:
    print("Error occurred while creating tables:", e)
    conn.rollback()  # Rollback changes on error
finally:
    cur.close()  # Close the cursor
    conn.close()  # Close the connection
