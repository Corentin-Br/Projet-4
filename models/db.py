from tinydb import TinyDB, Query

database = TinyDB("db.json")
tournament_tables = database.table("tournaments")
member_tables = database.table("members")
query = Query()
