from model import Partido, Jornada, Equipo
from google.appengine.ext import db

query = Jornada.all(keys_only=True)
entries =query.fetch(1000)
db.delete(entries)

query = Partido.all(keys_only=True)
entries =query.fetch(1000)
db.delete(entries)

query = Equipo.all(keys_only=True)
entries =query.fetch(1000)
db.delete(entries)