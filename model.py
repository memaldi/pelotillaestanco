from google.appengine.ext import db
from google.appengine.api import users

class Usuario(db.Model):
	#user = db.UserProperty()
	user_id = db.StringProperty()
	email = db.EmailProperty()
	nick = db.StringProperty()
	admin = db.BooleanProperty()
	activo = db.BooleanProperty()

class Equipo(db.Model):
	nombre = db.StringProperty()
	lfp = db.BooleanProperty()
	champions = db.BooleanProperty()
	uefa = db.BooleanProperty()

class Jornada(db.Model):
	numero = db.IntegerProperty()
	fecha_inicio = db.DateTimeProperty()

class Partido(db.Model):
	local = db.ReferenceProperty(reference_class=Equipo, collection_name='local')
	visitante = db.ReferenceProperty(reference_class=Equipo, collection_name='visitante')
	jornada = db.ReferenceProperty(reference_class=Jornada)

class GolesPartidoEquipo(db.Model):
	equipo = db.ReferenceProperty(reference_class=Equipo)
	partido = db.ReferenceProperty(reference_class=Partido)
	goles = db.IntegerProperty()

class Jugador(db.Model):
	nombre = db.StringProperty()
	demarcacion = db.StringProperty()
	equipo = db.ReferenceProperty(reference_class=Equipo)

class PronosticoJornada(db.Model):
	jornada = db.ReferenceProperty(reference_class=Jornada)
	usuario = db.ReferenceProperty(reference_class=Usuario)

class PronosticoPartido(db.Model):
	partido = db.ReferenceProperty(reference_class=Partido)
	goles_local = db.IntegerProperty()
	goles_visitante = db.IntegerProperty()
	pronostico_jornada = db.ReferenceProperty(reference_class=PronosticoJornada)

class PronosticoJugador(db.Model):
	pronostico_jornada = db.ReferenceProperty(reference_class=PronosticoJornada)
	jugador = db.ReferenceProperty(reference_class=Jugador)
	goles = db.IntegerProperty()

class PronosticoGlobal(db.Model):
	campeon_invierno = db.ReferenceProperty(reference_class=Equipo, collection_name='campeon_invierno')
	campeon_copa = db.ReferenceProperty(reference_class=Equipo, collection_name='campeon_copa')
	campeon_liga = db.ReferenceProperty(reference_class=Equipo, collection_name='campeon_liga')
	puesto_champions = db.ReferenceProperty(reference_class=Equipo, collection_name='puesto_champions')
	puestos_uefa = db.ListProperty(db.Key)
	puestos_descenso = db.ListProperty(db.Key)
	zamora = db.ReferenceProperty(reference_class=Jugador, collection_name='zamora')
	campeon_champions = db.ReferenceProperty(reference_class=Equipo, collection_name='campeon_champions')
	campeon_uefa = db.ReferenceProperty(reference_class=Equipo, collection_name='campeon_uefa')