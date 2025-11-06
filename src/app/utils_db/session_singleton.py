import src.db.orm as db

class SessionSingleton:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.session = db.Session()
        return cls._instance
