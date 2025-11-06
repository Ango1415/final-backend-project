import psycopg2
from hashlib import sha1

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


insert_users_records = "INSERT INTO users (username, password) VALUES (%s, %s)"
insert_projects_records = "INSERT INTO projects (name, description, owner) VALUES (%s, %s, %s)"
insert_project_participants_records = "INSERT INTO project_participants (user_id, project_id) VALUES (%s, %s)"
users = [
    ("angel_gomez", sha1('123'.encode()).hexdigest()),
    ("fabian_estupinan", sha1('234'.encode()).hexdigest()),
]
projects = [
    ('first_project', 'First project made for testing', 1),
    ('second_project', 'Second project made for testing', 1),
    ('main_project', 'Third project made for testing', 2)
]

project_participants = [
    (1, 1),
    (1, 2),
    (2, 2),
    (2, 3)
]

if __name__ == '__main__':
    # Execute SQL commands to populate tables
    try:
        cur.executemany(insert_users_records, users)
        cur.executemany(insert_projects_records, projects)
        cur.executemany(insert_project_participants_records, project_participants)
        conn.commit()
        print("Records inserted successfully")
    except Exception as e:
        print("Error occurred while inserting records:", e)
        conn.rollback()  # Rollback changes on error
    finally:
        cur.close()  # Close the cursor
        conn.close()  # Close the connection
