import keyring

def set_user(user):
    keyring.set_password("mylittelpyapp", "db-user", user)

def set_password(password):
    keyring.set_password("mylittelpyapp", "db-pw", password)

def set_server(server):
    keyring.set_password("mylittelpyapp", "db-server", server)

def set_db(db):
    keyring.set_password("mylittelpyapp", "db-db", db)


def get_user():
    return keyring.get_password("mylittelpyapp", "db-user")

def get_password():
    return keyring.get_password("mylittelpyapp", "db-pw")

def get_server():
    return keyring.get_password("mylittelpyapp", "db-server")

def get_db():
    return keyring.get_password("mylittelpyapp", "db-db")
