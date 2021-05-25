"""Implement all operations on the database"""
from tinydb import TinyDB, Query

DATABASE = TinyDB("models/db.json")
TOURNAMENT_TABLES = DATABASE.table("tournaments")
MEMBER_TABLES = DATABASE.table("members")
QUERY = Query()
