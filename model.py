from google.appengine.ext import ndb
from google.appengine.api import users

class Usuario(ndb.Model):
	user = ndb.UserProperty()
	admin = ndb.BooleanProperty()

class Equipo(ndb.Model):
	nombre = ndb.StringProperty()
	lfp = ndb.BooleanProperty()
	champions = ndb.BooleanProperty()
	uefa = ndb.BooleanProperty()

class Jornada(ndb.Model):
	numero = ndb.IntegerProperty()
	fecha = ndb.DateProperty()
	fecha_limite = ndb.DateTimeProperty()

class Partido(ndb.Model):
	local = ndb.ReferenceProperty(reference_class=Equipo)
	visitante = ndb.ReferenceProperty(reference_class=Equipo)
	jornada = ndb.ReferenceProperty(reference_class=Jornada)

class GolesPartidoEquipo(ndb.Model):
	equipo = ndb.ReferenceProperty(reference_class=Equipo)
	partido = ndb.ReferenceProperty(reference_class=Partido)
	goles = ndb.IntegerProperty()

class Jugador(ndb.Model):
	nombre = ndb.StringProperty()
	demarcacion = ndb.StringProperty()

class PronosticoJornada(ndb.Model):
	jornada = ndb.ReferenceProperty(reference_class=Jornada)
	usuario = ndb.ReferenceProperty(reference_class=Usuario)

class PronosticoPartido(ndb.Model):
	partido = ndb.ReferenceProperty(reference_class=Partido)
	goles_local = ndb.IntegerProperty()
	goles_visitante = ndb.IntegerProperty()
	pronostico_jornada = ndb.ReferenceProperty(reference_class=PronosticoJornada)

class PronosticoJugador(ndb.Model):
	pronostico_jornada = ndb.ReferenceProperty(reference_class=PronosticoJornada)
	jugador = ndb.ReferenceProperty(reference_class=Jugador)
	goles =ndb.IntegerProperty()

class PronosticoGlobal(ndb.Model):
	campeon_invierno = ndb.ReferenceProperty(reference_class=Equipo)
	campeon_copa = ndb.ReferenceProperty(reference_class=Equipo)
	campeon_liga = ndb.ReferenceProperty(reference_class=Equipo)
	puesto_champions = ndb.ReferenceProperty(reference_class=Equipo)
	puestos_uefa = ndb.ListProperty(ndb.Key)
	puestos_descenso = ndb.ListProperty(ndb.Key)
	zamora = ndb.ReferenceProperty(reference_class=Jugador)
	campeon_champions = ndb.ReferenceProperty(reference_class=Equipo)
	campeon_uefa = ndb.ReferenceProperty(reference_class=Equipo)