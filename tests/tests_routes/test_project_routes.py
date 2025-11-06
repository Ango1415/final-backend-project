from unittest.mock import patch

import src.app.routes.project_routes as project_routes
import src.db.orm as db
from src.app.models import models


class TestIntegration:

    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.read_participant_projects")
    @patch("src.app.auth.auth.Authenticator.authentication")
    def test_get_projects(self, mock_authentication, mock_read_projects):
        user = db.User(username="test", password="password")
        project = db.Project(project_id=1, name="test", description="description", owner=1)
        projects = [project, project]

        mock_authentication.return_value = user
        mock_read_projects.return_value = projects

        values = project_routes.get_projects(user)

        assert isinstance(values, list)
        for value in values: assert isinstance(value, models.ProjectOut)

    # TODO: Add the additional test cases for get_projects functionality

    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.create_project")
    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.read_project_by_project_name_user")
    @patch("src.app.auth.auth.Authenticator.authentication")
    def test_create_project(self, mock_authentication, mock_read_project, mock_create_project):
        user = db.User(username="test", password="password")
        project = models.ProjectIn(name="test", description="description")
        mock_read_project.return_value = None

        value = project_routes.create_project(project, user)

        assert mock_read_project.called
        assert mock_create_project.called
        assert isinstance(value, dict)
        assert value == {'message': f"Project '{project.name}' successfully created."}

    # TODO: Add the additional test cases for create_project functionality

    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.validate_project_participant")
    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.read_project_by_project_id")
    @patch("src.app.auth.auth.Authenticator.authentication")
    def test_get_project_details(self, mock_authentication, mock_read_project, mock_project_participant):
        user = db.User(username="test", password="password")
        project_id = 1
        project_db = db.Project(project_id=project_id, name="test", description="description", owner=1)
        mock_project_participant.return_value = True
        mock_read_project.return_value = project_db

        value = project_routes.get_project_details(project_id, user)

        assert mock_project_participant.called
        assert mock_read_project.called
        assert isinstance(value, models.ProjectOut)

    # TODO: Add the additional test cases for get_project_details functionality

    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.validate_project_participant")
    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.update_project")
    @patch("src.app.auth.auth.Authenticator.authentication")
    def test_update_project_details(self, mock_authentication, mock_update_project, mock_project_participant):
        user = db.User(username="test", password="password")
        project_id = 1
        project_in = models.ProjectIn(name="test", description="description")
        mock_project_participant.return_value = True

        value = project_routes.update_project_details(project_id, project_in, user)

        assert value  == {'message': 'Project details updated successfully.'}

    # TODO: Add the additional test cases for update_project_details functionality

    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.delete_project")
    @patch("src.app.auth.auth.Authenticator.authentication")
    def test_delete_project(self, mock_authentication, mock_delete_project):
        user = db.User(username="test", password="password")
        project_id = 1

        value = project_routes.delete_project(project_id, user)

        assert isinstance(value, dict)
        assert value == {'message': 'Project deleted successfully.'}
        assert mock_delete_project.called

    # TODO: Add the additional test cases for delete_project functionality

    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.create_project_participation")
    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.read_project_by_project_id")
    @patch("src.app.utils_db.utils_db_user.utils_db_user_impl.UtilsDbUserImpl.read_user_by_username")
    @patch("src.app.auth.auth.Authenticator.authentication")
    def test_grant_access_to_user(self, mock_authentication, mock_read_user, mock_read_project, mock_create_participation):
        user = db.User(user_id=1, username="test", password="password")
        project = db.Project(project_id=1, name="test", description="description", owner=1)
        project_id = 1
        username = "test"
        mock_read_project.return_value = project

        value = project_routes.grant_access_to_user(project_id, username, user)

        assert value == {'message': f"You've granted access to '{username}' to use this project."}
        assert mock_read_user.called
        assert mock_read_project.called
        assert mock_create_participation.called

    # TODO: Add the additional test cases for grant_access_to_user functionality