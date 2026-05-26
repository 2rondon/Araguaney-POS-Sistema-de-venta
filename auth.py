import database

class SessionManager:
    _current_user = None

    @classmethod
    def login(cls, username, password):
        conn = database.get_connection()
        user = conn.execute("SELECT id, username, nombre, rol FROM usuarios WHERE username = ? AND password = ?", 
                            (username, password)).fetchone()
        conn.close()
        if user:
            cls._current_user = {"id": user["id"], "username": user["username"], "nombre": user["nombre"], "rol": user["rol"]}
            return True
        return False

    @classmethod
    def logout(cls):
        cls._current_user = None

    @classmethod
    def get_user(cls):
        return cls._current_user

    @classmethod
    def is_admin(cls):
        return cls._current_user is not None and cls._current_user["rol"] == "ADMIN"