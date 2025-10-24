from sqlalchemy import create_engine, String, ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship
from hashlib import sha1

CREATE_TABLES = False

# Set up the db connection
username = 'postgres'
password = 'admin'
host = 'localhost'  # or the IP address of your PostgresSQL server
port = '5432'       # default PostgresSQL port
database = 'python_web'

engine = create_engine(f'postgresql://{username}:{password}@{host}:{port}/{database}')

# Define the base class
class Base(DeclarativeBase):
    def to_dict(self):
        return {key:value for key, value in self.__dict__.items() if key != '_sa_instance_state'}

# Define the Product class mapped to the 'products' table
class User(Base):
    __tablename__ = 'users'
    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)

    # Define a relationship to the User model
    projects: Mapped[list["Project"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    # Define relationship with ProjectParticipant model
    project_participants: Mapped[list["ProjectParticipant"]] = relationship(back_populates="user",
                                                                            cascade="all, delete-orphan")

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
    owner: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)

    # Define a relationship to the User model
    user: Mapped[User] = relationship(back_populates="projects")
    # Define relationship with Document model
    documents: Mapped[list["Document"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    # Define relationship with ProjectParticipant model
    project_participants: Mapped[list["ProjectParticipant"]] = relationship(back_populates="project",
                                                                            cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"""Project(
            project_id={self.project_id!r}, 
            name={self.name!r}, 
            owner={self.user!r}), 
            description={self.description!r}
        )"""

class Document(Base):
    __tablename__ = 'documents'
    document_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    format: Mapped[str] = mapped_column(String(50), nullable=False)
    file_url: Mapped[str] = mapped_column(String(200), nullable=False)
    attached_project: Mapped[int] = mapped_column(ForeignKey('projects.project_id', ondelete='CASCADE'),
                                                  nullable=False)

    # Define relationship with Project model
    project: Mapped[Project] = relationship(back_populates="documents")

    def __repr__(self) -> str:
        return f"""Document(
            document_id={self.document_id!r}, 
            name={self.name!r}, 
            format={self.format!r}, 
            file_url={self.file_url!r}, 
            attached_project={self.project!r}, 
        )"""

class ProjectParticipant(Base):
    __tablename__ = 'project_participants'
    proj_part_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.project_id', ondelete='CASCADE'),
                                            nullable=False)

    # Define relationship with User model
    user: Mapped[User] = relationship(back_populates="project_participants")
    #Define relationship with Project model
    project: Mapped[Project] = relationship(back_populates="project_participants")

    def __repr__(self) -> str:
        return f"""ProjectParticipant(
            proj_part_id={self.proj_part_id!r}, 
            user_id={self.user_id!r}, 
            project_id={self.project_id!r}, 
            user={self.user!r}),
            project={self.project!r})
        )"""




# Set up the db session
Session = sessionmaker(bind=engine)


if CREATE_TABLES:
    Base.metadata.create_all(engine)
    session = Session()
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

    project_participant = ProjectParticipant(user_id=1, project_id=1)
    session.add(project_participant)
    project_participant = ProjectParticipant(user_id=1, project_id=2)
    session.add(project_participant)
    project_participant = ProjectParticipant(user_id=2, project_id=2)
    session.add(project_participant)
    project_participant = ProjectParticipant(user_id=2, project_id=3)
    session.add(project_participant)
    session.commit()

if __name__ == '__main__':
    session = Session()

    result:Document = session.execute(select(Document).where(Document.document_id == 7)).scalar_one_or_none()

    print(result.to_dict())

    session.close()
