from http import HTTPStatus
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from src.app.utils_db.utils_db_project.utils_db_project_impl import UtilsDbProjectImpl


# class UserDummy:
#     pass

class ProjectDummy:
    def __init__(self):
        self.name = None
        self.description = None
    pass

class ProjectParticipantDummy:
    def __init__(self):
        self.project = ProjectDummy()

class TestUnitary:

    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    @patch("src.db.orm.ProjectParticipant")
    @patch("src.db.orm.Project")
    def test_create_project(self, mock_project, mock_project_participant, mock_session_singleton):
        utils_db_project = UtilsDbProjectImpl(mock_session_singleton)
        utils_db_project.create_project(mock_project)
        assert mock_session_singleton.session.add.call_count == 2
        assert mock_session_singleton.session.commit.call_count == 2
        assert mock_project_participant.called

    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    @patch("src.db.orm.ProjectParticipant")
    @patch("src.db.orm.Project")
    def test_create_project_exception(self, mock_project, mock_project_participant, mock_session_singleton):
        mock_project_participant.side_effect = Exception
        utils_db_project = UtilsDbProjectImpl(mock_session_singleton)
        with pytest.raises(HTTPException) as expected:
            utils_db_project.create_project(mock_project)
        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert expected.value.detail == f"ERROR - Project creation failed: 'No access to db, try again later'"

    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    @patch("src.db.orm.User")
    def test_read_participant_projects(self, mock_user, mock_session_singleton):
        project_participant = ProjectParticipantDummy()
        project_participants = [project_participant, project_participant]

        mock_execute = mock_session_singleton.session.execute.return_value
        mock_scalars = mock_execute.scalars.return_value
        mock_scalars.all.return_value = project_participants

        utils_db_project = UtilsDbProjectImpl(mock_session_singleton)
        value = utils_db_project.read_participant_projects(mock_user)

        assert type(value) == list
        assert mock_session_singleton.session.execute.called

    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    @patch("src.db.orm.User")
    def test_read_participant_projects_exception(self, mock_user, mock_session_singleton):
        project_participant = ProjectParticipantDummy()
        project_participants = [project_participant, project_participant]

        mock_execute = mock_session_singleton.session.execute.return_value
        mock_scalars = mock_execute.scalars.return_value
        mock_scalars.all.return_value = project_participants
        mock_scalars.all.side_effect = Exception

        utils_db_project = UtilsDbProjectImpl(mock_session_singleton)
        with pytest.raises(HTTPException) as expected:
            utils_db_project.read_participant_projects(mock_user)
        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert expected.value.detail == 'No access to db, try again later'

    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    @patch("src.db.orm.User")
    def test_read_project_by_project_name_user(self, mock_user, mock_session_singleton):
        project_name= 'test'
        project = ProjectDummy()
        mock_execute = mock_session_singleton.session.execute.return_value
        mock_execute.scalar_one_or_none.return_value = project

        utils_db_project = UtilsDbProjectImpl(mock_session_singleton)
        value = utils_db_project.read_project_by_project_name_user(project_name, mock_user)

        assert type(value) == ProjectDummy
        assert mock_session_singleton.session.execute.called

    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    @patch("src.db.orm.User")
    def test_read_project_by_project_name_user_exception(self, mock_user, mock_session_singleton):
        project_name= 'test'
        project = ProjectDummy()
        mock_execute = mock_session_singleton.session.execute.return_value
        mock_execute.scalar_one_or_none.return_value = project
        mock_execute.scalar_one_or_none.side_effect = Exception

        utils_db_project = UtilsDbProjectImpl(mock_session_singleton)
        with pytest.raises(HTTPException) as expected:
            utils_db_project.read_project_by_project_name_user(project_name, mock_user)
        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert expected.value.detail == 'No access to db, try again later'

    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    def test_read_project_by_project_id(self, mock_session_singleton):
        project_id = 1
        project = ProjectDummy()
        mock_execute = mock_session_singleton.session.execute.return_value
        mock_execute.scalar_one_or_none.return_value = project

        utils_db_project = UtilsDbProjectImpl(mock_session_singleton)
        value = utils_db_project.read_project_by_project_id(project_id)

        assert type(value) == ProjectDummy
        assert mock_session_singleton.session.execute.called

    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    def test_read_project_by_project_id_exception(self, mock_session_singleton):
        project_id = 1
        project = ProjectDummy()
        mock_execute = mock_session_singleton.session.execute.return_value
        mock_execute.scalar_one_or_none.return_value = project
        mock_execute.scalar_one_or_none.side_effect = Exception

        utils_db_project = UtilsDbProjectImpl(mock_session_singleton)
        with pytest.raises(HTTPException) as expected:
            utils_db_project.read_project_by_project_id(project_id)
        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert expected.value.detail == 'No access to db, try again later'

    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.read_project_by_project_id")
    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    def test_update_project(self, mock_session_singleton, mock_read_project):
        project_id = 1
        project_name = 'test'
        project_description = 'description'
        project = ProjectDummy()
        mock_read_project.return_value = project

        utils_db_project = UtilsDbProjectImpl(mock_session_singleton)
        utils_db_project.update_project(project_id, project_name, project_description)

        assert mock_session_singleton.session.commit.called
        assert mock_read_project.called
        assert project.name == project_name
        assert project.description == project_description

    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.read_project_by_project_id")
    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    def test_update_project_not_found(self, mock_session_singleton, mock_read_project):
        project_id = 1
        project_name = 'test'
        project_description = 'description'
        mock_read_project.return_value = None

        utils_db_project = UtilsDbProjectImpl(mock_session_singleton)
        with pytest.raises(HTTPException) as expected:
            utils_db_project.update_project(project_id, project_name, project_description)
        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.NOT_FOUND
        assert expected.value.detail == 'No project able to apply this process was found with that id. Try it again.'

    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.read_project_by_project_id")
    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    def test_update_project_exception(self, mock_session_singleton, mock_read_project):
        project_id = 1
        project_name = 'test'
        project_description = 'description'
        project = ProjectDummy()
        mock_read_project.return_value = project
        mock_session_singleton.session.commit.side_effect = Exception

        utils_db_project = UtilsDbProjectImpl(mock_session_singleton)
        with pytest.raises(HTTPException) as expected:
            utils_db_project.update_project(project_id, project_name, project_description)
        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert expected.value.detail == 'No access to db, try again later.'
        assert mock_session_singleton.session.rollback.called

    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.read_project_by_project_id")
    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    @patch("src.db.orm.User")
    def test_delete_project(self, mock_user, mock_session_singleton, mock_read_project):
        project_id = 1
        owner_id = 2
        project = ProjectDummy()
        project.owner = owner_id
        mock_user.user_id = owner_id
        mock_read_project.return_value = project

        utils_db_project = UtilsDbProjectImpl(mock_session_singleton)
        utils_db_project.delete_project(project_id, mock_user)

        assert mock_session_singleton.session.delete.called
        assert mock_session_singleton.session.commit.called
        assert mock_read_project.called

    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.read_project_by_project_id")
    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    @patch("src.db.orm.User")
    def test_delete_project_not_found(self, mock_user, mock_session_singleton, mock_read_project):
        project_id = 1
        owner_id = 2
        mock_user.user_id = owner_id
        mock_read_project.return_value = None

        utils_db_project = UtilsDbProjectImpl(mock_session_singleton)
        with pytest.raises(HTTPException) as expected:
            utils_db_project.delete_project(project_id, mock_user)
        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.NOT_FOUND
        assert expected.value.detail == 'No project able to apply this process was found with that id. Try it again.'

    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.read_project_by_project_id")
    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    @patch("src.db.orm.User")
    def test_delete_project_exception(self, mock_user, mock_session_singleton, mock_read_project):
        project_id = 1
        owner_id = 2
        project = ProjectDummy()
        project.owner = owner_id
        mock_user.user_id = owner_id
        mock_read_project.return_value = project
        mock_session_singleton.session.commit.side_effect = Exception

        utils_db_project = UtilsDbProjectImpl(mock_session_singleton)
        with pytest.raises(HTTPException) as expected:
            utils_db_project.delete_project(project_id, mock_user)
        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert expected.value.detail == 'No access to db, try again later.'
        assert mock_session_singleton.session.rollback.called

    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    @patch("src.db.orm.User")
    def test_validate_project_participant(self, mock_user, mock_session_singleton):
        project_id = 1
        project_participant = ProjectParticipantDummy()
        mock_execute = mock_session_singleton.session.execute.return_value
        mock_execute.scalar_one_or_none.return_value = project_participant

        utils_db_project = UtilsDbProjectImpl(mock_session_singleton)
        value = utils_db_project.validate_project_participant(1, mock_user)

        assert mock_session_singleton.session.execute.called
        assert isinstance(value, ProjectParticipantDummy)

    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    @patch("src.db.orm.User")
    def test_validate_project_participant_exception(self, mock_user, mock_session_singleton):
        project_id = 1
        project_participant = ProjectParticipantDummy()
        mock_execute = mock_session_singleton.session.execute.return_value
        mock_execute.scalar_one_or_none.return_value = project_participant
        mock_execute.scalar_one_or_none.side_effect = Exception

        utils_db_project = UtilsDbProjectImpl(mock_session_singleton)
        with pytest.raises(HTTPException) as expected:
            value = utils_db_project.validate_project_participant(1, mock_user)
        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert expected.value.detail == 'No access to db, try again later.'

    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.read_project_by_project_id")
    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.validate_project_participant")
    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    @patch("src.db.orm.User")
    @patch("src.db.orm.User")
    @patch("src.db.orm.ProjectParticipant")
    def test_create_project_participation(self, mock_participation, mock_user_participant, mock_user_owner,
                                          mock_session_singleton, mock_validate_participation, mock_read_project):
        project_id = 1
        owner_id = 2
        project = ProjectDummy()
        project_participant = ProjectParticipantDummy()
        project.owner = owner_id

        mock_user_owner.user_id = owner_id
        mock_read_project.return_value = project
        mock_validate_participation.return_value = None
        mock_participation.return_value = project_participant

        utils_db_project = UtilsDbProjectImpl(mock_session_singleton)
        utils_db_project.create_project_participation(project_id, mock_user_participant, mock_user_owner)

        assert mock_read_project.called
        assert mock_validate_participation.called
        assert mock_participation.called
        assert mock_session_singleton.session.add.called
        assert mock_session_singleton.session.commit.called

    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.read_project_by_project_id")
    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.validate_project_participant")
    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    @patch("src.db.orm.User")
    @patch("src.db.orm.User")
    @patch("src.db.orm.ProjectParticipant")
    def test_create_project_participation_conflict(self, mock_participation, mock_user_participant, mock_user_owner,
                                          mock_session_singleton, mock_validate_participation, mock_read_project):
        project_id = 1
        owner_id = 2
        project = ProjectDummy()
        project_participant = ProjectParticipantDummy()
        project.owner = owner_id

        mock_user_owner.user_id = owner_id
        mock_read_project.return_value = project
        mock_validate_participation.return_value = project_participant
        mock_participation.return_value = None

        utils_db_project = UtilsDbProjectImpl(mock_session_singleton)
        with pytest.raises(HTTPException) as expected:
            utils_db_project.create_project_participation(project_id, mock_user_participant, mock_user_owner)

        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.CONFLICT
        assert mock_read_project.called

    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.read_project_by_project_id")
    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.validate_project_participant")
    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    @patch("src.db.orm.User")
    @patch("src.db.orm.User")
    @patch("src.db.orm.ProjectParticipant")
    def test_create_project_participation_exception(self, mock_participation, mock_user_participant, mock_user_owner,
                                          mock_session_singleton, mock_validate_participation, mock_read_project):
        project_id = 1
        owner_id = 2
        other_user_id = 3
        project = ProjectDummy()
        project_participant = ProjectParticipantDummy()
        project.owner = owner_id

        mock_user_owner.user_id = other_user_id
        mock_read_project.return_value = project
        mock_validate_participation.return_value = None
        mock_participation.return_value = project_participant

        utils_db_project = UtilsDbProjectImpl(mock_session_singleton)
        with pytest.raises(HTTPException) as expected:
            utils_db_project.create_project_participation(project_id, mock_user_participant, mock_user_owner)

        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.UNAUTHORIZED


    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.read_project_by_project_id")
    @patch("src.app.utils_db.utils_db_project.utils_db_project_impl.UtilsDbProjectImpl.validate_project_participant")
    @patch("src.app.utils_db.session_singleton.SessionSingleton")
    @patch("src.db.orm.User")
    @patch("src.db.orm.User")
    @patch("src.db.orm.ProjectParticipant")
    def test_create_project_participation_exception(self, mock_participation, mock_user_participant, mock_user_owner,
                                          mock_session_singleton, mock_validate_participation, mock_read_project):
        project_id = 1
        owner_id = 2
        project = ProjectDummy()
        project_participant = ProjectParticipantDummy()
        project.owner = owner_id

        mock_user_owner.user_id = owner_id
        mock_read_project.return_value = project
        mock_validate_participation.return_value = None
        mock_validate_participation.side_effect = Exception
        mock_participation.return_value = project_participant

        utils_db_project = UtilsDbProjectImpl(mock_session_singleton)
        with pytest.raises(HTTPException) as expected:
            utils_db_project.create_project_participation(project_id, mock_user_participant, mock_user_owner)

        assert isinstance(expected.value, HTTPException)
        assert expected.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert mock_session_singleton.session.rollback.called
