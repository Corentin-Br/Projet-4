from tinydb import TinyDB, Query

database = TinyDB("models/db.json")
tournament_tables = database.table("tournaments")
member_tables = database.table("members")
QUERY = Query()
