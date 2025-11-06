from src.app.utils_db.session_singleton import SessionSingleton

class UtilsDb:
    def __init__(self, session: SessionSingleton):
        self.session = session
