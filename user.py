# BODO - A production data explorer
#
# Copyright (C) 2024  Jens Hofer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
