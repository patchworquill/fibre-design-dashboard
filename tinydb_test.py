from tinydb import TinyDB, Query

db = TinyDB('./db.json')
User = Query()
db.insert({'struc': 'SB-1141A3-1', 'stype': 'FOSC-450-BS'})
db.search(User.struc == 'SB-1141A3-1')