from sqlalchemy import create_engine, String, ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship
from hashlib import sha1

CREATE_TABLES = True

# Set up the database connection
username = 'postgres'
password = 'admin'
host = 'localhost'  # or the IP address of your PostgreSQL server
port = '5432'       # default PostgreSQL port
database = 'python_web'

engine = create_engine(f'postgresql://{username}:{password}@{host}:{port}/{database}')


# Define the base class
class Base(DeclarativeBase):
    pass
# Define the Product class mapped to the 'products' table
class User(Base):
    __tablename__ = 'users'
    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)

    # Define a relationship to the User model
    projects: Mapped[list["Project"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"""User(
            user_id={self.user_id!r}, 
            username={self.username!r}, 
            password={self.password!r})
        )"""

class Project(Base):
    __tablename__ = 'projects'
    project_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=True)
    owner: Mapped[int] = mapped_column(ForeignKey('users.user_id'), nullable=False)

    # Define a relationship to the User model
    user: Mapped[User] = relationship(back_populates="projects")

    def __repr__(self) -> str:
        return f"""Project(
            project_id={self.project_id!r}, 
            name={self.name!r}, 
            owner={self.user!r}), 
            description={self.description!r}
        )"""

# Set up the database session
Session = sessionmaker(bind=engine)
session = Session()

if CREATE_TABLES:
    Base.metadata.create_all(engine)

    # Populating db
    # Use SQLAlchemy to add a new product
    user = User(username='angel_gomez', password=sha1('123'.encode()).hexdigest())
    session.add(user)
    user = User(username='fabian_estupinan', password=sha1('234'.encode()).hexdigest())
    session.add(user)
    session.commit()

    project = Project(name='first_project', description='First project made for testing', owner=1)
    session.add(project)
    project = Project(name='second_project', description='Second project made for testing', owner=1)
    session.add(project)
    project = Project(name='main_project', description='Third project made for testing', owner=2)
    session.add(project)
    session.commit()


user = session.execute(select(User).where(User.username == 'angel_gomez')).scalar_one_or_none()
print(user)
print('----')
users = session.execute(select(User)).scalars().all()
for user in users:
    print(user)

