#!/usr/bin/env python
# -⁻- coding: UTF-8 -*-
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.api import users
from model import Usuario, Equipo, Jugador, Jornada, Partido, GolesPartidoEquipo, GolesJornadaJugador, PronosticoJornada, PronosticoPartido, PronosticoJugador, PronosticoGlobal
from google.appengine.ext import db
from HTMLParser import HTMLParser

import webapp2
import jinja2
import os
import time
import datetime
import re
import urllib

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

FECHA_LIMITE = 2

class MainHandler(webapp2.RequestHandler):
    def get(self):
    	user = users.get_current_user()
    	if user:
            # Crear el perfil si no existe
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario == None:
                usuario = Usuario(user_id=user.user_id(), email=user.email(), nick=user.nickname(), activo=False, admin=False)
                usuario.put()
            if not usuario.activo:
                template = JINJA_ENVIRONMENT.get_template('templates/espera.html')
                content = {'nick': usuario.nick, 'email': usuario.email, 'usuario': usuario}
                self.response.write(template.render(content))
                return

            content = {'usuario': usuario }
            template = JINJA_ENVIRONMENT.get_template('templates/main.html')
            self.response.write(template.render(content))
            return
        else:
    		self.redirect(users.create_login_url(self.request.uri))

class Admin(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    template = JINJA_ENVIRONMENT.get_template('templates/panel-admin.html')
                    content = {'usuario': usuario }
                    self.response.write(template.render(content))
                    return
        self.redirect('/')

class Jugadores(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    jugadores_list = Jugador.all()
                    jugadores_list.order("nombre")
                    content = {'jugadores': jugadores_list, 'usuario': usuario }
                    template = JINJA_ENVIRONMENT.get_template('templates/panel-jugadores.html')
                    self.response.write(template.render(content))
                    return
        self.redirect('/')

    def post(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    keys = self.request.arguments()
                    for key in keys:
                        jugador = Jugador.get(key)
                        db.delete(jugador)
                    self.redirect('/admin/jugadores')
                    return

        self.redirect('/')

class FichaJugador(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    template = JINJA_ENVIRONMENT.get_template('templates/jugador.html')
                    key = self.request.get('key')
                    content = {'usuario': usuario }
                    equipos_list = Equipo.all()
                    equipos_list.order("nombre")
                    content['equipos'] = equipos_list
                    if key != '':
                        jugador = Jugador.get(key)
                        content['jugador'] = jugador
                        self.response.write(template.render(content))
                    else:
                        self.response.write(template.render(content))
                    return
        self.redirect('/')

    def post(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    nombre = self.request.get('nombre')
                    demarcacion = self.request.get('demarcacion')
                    equipo = Equipo.get(self.request.get('equipo'))

                    if self.request.get('key') == '':
                        jugador = Jugador(nombre=nombre, demarcacion=demarcacion, equipo=equipo)
                        jugador.put()
                    else:
                        jugador = Jugador.get(self.request.get('key'))
                        jugador.nombre = nombre
                        jugador.demarcacion = demarcacion
                        jugador.equipo = equipo
                        db.put(jugador)

                    self.redirect('/admin/jugadores')
                    return
        self.redirect('/')

class BorrarJugador(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    key = self.request.get('key')
                    jugador = Jugador.get(key)
                    db.delete(jugador)
                    self.redirect('/admin/jugadores')
                    return
        self.redirect('/')

class Equipos(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    equipos_list = Equipo.all()
                    equipos_list.order("nombre")
                    content = {'equipos': equipos_list, 'usuario': usuario}
                    template = JINJA_ENVIRONMENT.get_template('templates/panel-equipos.html')
                    self.response.write(template.render(content))
                    return
        self.redirect('/')


    def post(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    keys = self.request.arguments()
                    for key in keys:
                        equipo = Equipo.get(key)
                        for jugador in equipo.jugador_set:
                            db.delete(jugador)
                        db.delete(equipo)
                    self.redirect('/admin/equipos')
                    return

        self.redirect('/')

class FichaEquipo(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    template = JINJA_ENVIRONMENT.get_template('templates/equipo.html')
                    key = self.request.get('key')
                    if key != '':
                        equipo = Equipo.get(key)
                        content = {'equipo': equipo, 'usuario': usuario}
                        self.response.write(template.render(content))
                    else:
                        self.response.write(template.render())
                    return
        self.redirect('/')

    def post(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    print self.request.get('key')

                    nombre = self.request.get('nombre')
                    lfp = False
                    uefa = False
                    champions = False
                    if self.request.get('lfp'):
                        lfp = True
                    if self.request.get('champions'):
                        champions = True
                    if self.request.get('uefa'):
                        uefa = True
                    if self.request.get('key') == '':
                        equipo = Equipo(nombre=nombre, lfp=lfp, champions=champions, uefa=uefa)
                        equipo.put()
                    else:
                        equipo = Equipo.get(self.request.get('key'))
                        equipo.nombre = nombre
                        equipo.lfp = lfp
                        equipo.champions = champions
                        equipo.uefa = uefa
                        db.put(equipo)

                    self.redirect('/admin/equipos')
                    return
        self.redirect('/')

class BorrarEquipo(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    key = self.request.get('key')
                    equipo = Equipo.get(key)
                    for jugador in equipo.jugador_set:
                            db.delete(jugador)
                    db.delete(equipo)
                    self.redirect('/admin/equipos')
                    return
        self.redirect('/')

class Jornadas(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    jornadas = Jornada.all()
                    jornadas.order("numero")
                    jornada_list = []
                    for jornada in jornadas:
                        completa = True
                        for partido in jornada.partido_set:
                            pass
                        jornada_list.append(jornada)
                    content = {'jornadas': jornada_list, 'usuario': usuario}
                    template = JINJA_ENVIRONMENT.get_template('templates/panel-jornadas.html')
                    self.response.write(template.render(content))
                    return
        self.redirect('/')

class FichaJornada(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    template = JINJA_ENVIRONMENT.get_template('templates/jornada.html')
                    key = self.request.get('key')
                    equipos = Equipo.all()
                    equipos.filter("lfp =", True)
                    if key != '':
                        jornada = Jornada.get(key)
                        partidos = jornada.partido_set
                        partidos_list = []
                        result_dict = {}
                        for partido in partidos:
                            partidos_list.append(partido)
                            result_dict[partido.key()] = {}
                            print partido.key()
                            golesPartido = GolesPartidoEquipo.all()
                            golesPartido.filter("partido =", partido)
                            golesLocal = golesPartido.filter("equipo =", partido.local)

                            golesPartido = GolesPartidoEquipo.all()
                            golesPartido.filter("partido =", partido)
                            golesVisitante = golesPartido.filter("equipo =", partido.visitante)
                            if golesLocal.get() != None and golesVisitante.get() != None:
                                print golesLocal.get().goles
                                result_dict[partido.key()]['local'] = int(golesLocal.get().goles)
                                result_dict[partido.key()]['visitante'] = int(golesVisitante.get().goles)
                            else:
                                result_dict[partido.key()]['local'] = None
                                result_dict[partido.key()]['visitante'] = None
                        if jornada.fecha_inicio != None:
                            fecha_str = '%sT%s' % (jornada.fecha_inicio.date(), jornada.fecha_inicio.time())
                        else:
                            fecha_str = None
                        content = {'jornada': jornada, 'partidos': partidos_list, 'equipos': equipos, 'fecha_str': fecha_str, 'result_dict': result_dict, 'usuario': usuario}
                        self.response.write(template.render(content))
                    else:
                        jornadas = Jornada.all()
                        jornadas.order('-numero')
                        ultima_jornada = jornadas.get()
                        numero = ultima_jornada.numero
                        if numero == None:
                            numero = 1
                        else:
                            numero += 1
                        content = {'rango': range(10), 'equipos': equipos, 'numero': numero, 'usuario': usuario}
                        self.response.write(template.render(content))
                    return
        self.redirect('/')

    def post(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    key = self.request.get('key')
                    numero = self.request.get('numero')
                    try:
                        fecha_struct = time.strptime(self.request.get('fecha'), "%Y-%m-%dT%H:%M:%S")
                    except:
                        fecha_struct = time.strptime(self.request.get('fecha') + ':00', "%Y-%m-%dT%H:%M:%S")
                    fecha = datetime.datetime(year=fecha_struct.tm_year, month=fecha_struct.tm_mon, day=fecha_struct.tm_mday, hour=fecha_struct.tm_hour, minute=fecha_struct.tm_min, second=fecha_struct.tm_sec)
                    if key != '':
                        jornada = Jornada.get(key)
                        jornada.numero = int(numero)
                        jornada.fecha_inicio = fecha
                        db.put(jornada)
                        partido_key_set = set()
                        for arg in self.request.arguments():
                            if arg.startswith('local-'):
                                partido_key = arg.replace('local-', '')
                                partido_key_set.add(partido_key)
                        for partido_key in partido_key_set:
                            partido = Partido.get(partido_key)
                            local_id = self.request.get('local-%s' % partido_key)
                            visitante_id = self.request.get('visitante-%s' % partido_key)
                            goles_local = self.request.get('goles-local-%s' % partido_key)
                            goles_visitante = self.request.get('goles-visitante-%s' % partido_key)

                            local = Equipo.get(local_id)
                            visitante = Equipo.get(visitante_id)
                            if goles_local != '' and goles_visitante != '':

                                golesPartidoLocal = GolesPartidoEquipo.all()
                                golesPartidoLocal.filter("partido =", partido)
                                golesPartidoLocal.filter("equipo =", local)
                                golesPartidoLocal = golesPartidoLocal.get()

                                golesPartidoVisitante = GolesPartidoEquipo.all()
                                golesPartidoVisitante.filter("partido =", partido)
                                golesPartidoVisitante.filter("equipo =", visitante)
                                golesPartidoVisitante = golesPartidoVisitante.get()

                                if golesPartidoLocal == None:
                                    golesPartidoLocal = GolesPartidoEquipo(equipo=local, partido=partido, goles=int(goles_local))
                                    golesPartidoLocal.put()
                                else:
                                    golesPartidoLocal.goles = int(goles_local)
                                    golesPartidoLocal.equipo = local
                                    db.put(golesPartidoLocal)

                                if golesPartidoVisitante == None:
                                    golesPartidoVisitante = GolesPartidoEquipo(equipo=visitante, partido=partido, goles=int(goles_visitante))
                                    golesPartidoVisitante.put()
                                else:
                                    golesPartidoVisitante.goles = int(goles_visitante)
                                    golesPartidoVisitante.equipo = visitante
                                    db.put(golesPartidoVisitante)

                            partido.local = local
                            partido.visitante = visitante
                            partido.jornada = jornada
                            db.put(partido)


                    else:
                        numero = self.request.get('numero')
                        jornada = Jornada(numero=numero, fecha=fecha)
                        jornada.put()
                        for item in range(10):
                            local_id = self.request.get('local-%s' % item)
                            visitante_id = self.request.get('visitante-%s' % item)
                            goles_local = self.request.get('goles-local-%s' % item)
                            goles_visitante = self.request.get('goles-visitante-%s' % item)

                            local = Equipo.get(local_id)
                            visitante = Equipo.get(visitante_id)
                            partido = Partido(local=local, visitante=visitante, jornada=jornada)
                            partido.put()

                            if goles_local != '' and goles_visitante != '':
                                golesPartidoLocal = GolesPartidoEquipo(equipo=local, partido=partido, goles=int(goles_local))
                                golesPartidoLocal.put()
                                golesPartidoVisitante = GolesPartidoEquipo(equipo=visitante, partido=partido, goles=int(goles_visitante))
                                golesPartidoVisitante.put()
                    self.redirect('/admin/jornadas')
                    return

        self.redirect('/')

class BorrarJornada(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    key = self.request.get('key')
                    jornada = Jornada.get(key)
                    for goleador in jornada.golesjornadajugador_set:
                        db.delete(goleador)

                    for partido in jornada.partido_set:
                        db.delete(partido)

                    db.delete(jornada)

                    self.redirect('/admin/jornadas')
                    return
        self.redirect('/')


class Goleadores(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    jornada_key = self.request.get('key')
                    jornada = Jornada.get(jornada_key)
                    content = {'goleadores': jornada.golesjornadajugador_set, 'jornada_key': jornada_key, 'usuario': usuario}
                    template = JINJA_ENVIRONMENT.get_template('templates/panel-goleadores.html')
                    self.response.write(template.render(content))
                    return
        self.redirect('/')

    def post(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    keys = self.request.arguments()
                    for key in keys:
                        if key != 'jornada_key':
                            goleador = GolesJornadaJugador.get(key)
                            db.delete(goleador)
                    self.redirect('/admin/jornadas/goleadores?key=%s' % self.request.get('jornada_key'))
                    return

class FichaGoleador(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    template = JINJA_ENVIRONMENT.get_template('templates/goleador.html')
                    key = self.request.get('key')
                    jornada_key = self.request.get('jornada')
                    jugadores = Jugador.all()
                    if key != '':
                        goleador = GolesJornadaJugador.get(key)
                        content = {'jugadores': jugadores, 'jornada_key': jornada_key, 'goleador': goleador, 'usuario': usuario}
                        self.response.write(template.render(content))
                        return
                    else:
                        content = {'jugadores': jugadores, 'jornada_key': jornada_key, 'usuario': usuario}
                        self.response.write(template.render(content))
                        return
        self.redirect('/')

    def post(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    key = self.request.get('key')
                    jugador_key = self.request.get('jugador')
                    jugador = Jugador.get(jugador_key)
                    goles = self.request.get('goles')
                    jornada_key = None
                    if key != '':
                        goleador = GolesJornadaJugador.get(key)
                        goleador.jugador = jugador
                        goleador.goles = int(goles)
                        db.put(goleador)
                        jornada_key = goleador.jornada.key()
                    else:
                        jornada_key = self.request.get('jornada_key')
                        jornada = Jornada.get(jornada_key)
                        goleador = GolesJornadaJugador(jornada=jornada, jugador=jugador, goles=int(goles))
                        goleador.put()
                    self.redirect('/admin/jornadas/goleadores?key=%s' % jornada_key)
                    return
        self.redirect('/')

class BorrarGoleador(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    jornada_key = self.request.get('jornada')
                    key = self.request.get('key')
                    goleador = GolesJornadaJugador.get(key)
                    db.delete(goleador)
                    self.redirect('/admin/jornadas/goleadores?key=%s' % jornada_key)
                    return
        self.redirect('/')

class Usuarios(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    usuarios = Usuario.all()
                    content = {'usuarios': usuarios, 'usuario': usuario}
                    template = JINJA_ENVIRONMENT.get_template('templates/panel-usuarios.html')
                    self.response.write(template.render(content))
                    return
        self.redirect('/')

class FichaUsuario(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    template = JINJA_ENVIRONMENT.get_template('templates/usuario.html')
                    key = self.request.get('key')
                    usuario = Usuario.get(key)
                    content = {'usuario_item': usuario, 'usuario': usuario}
                    self.response.write(template.render(content))
                    return
        self.redirect('/')

    def post(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    key = self.request.get('key')
                    admin = self.request.get('admin')
                    activo = self.request.get('activo')
                    usuario = Usuario.get(key)
                    usuario.activo = activo
                    usuario.admin = admin
                    db.put(usuario)
                    self.redirect('/admin/usuarios')
                    return
        self.redirect('/')

class Pronosticos(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.activo:
                    jornadas = Jornada.all()
                    jornadas.order("numero")
                    fecha_limite_dict = {}
                    for jornada in jornadas:
                        if jornada.fecha_inicio == None:
                            fecha_limite_dict[jornada.key()] = jornada.fecha_inicio
                        else:
                            fecha_limite_dict[jornada.key()] = jornada.fecha_inicio - datetime.timedelta(hours=2)
                    content = {'jornadas': jornadas, 'fecha_limite_dict': fecha_limite_dict, 'usuario': usuario}
                    template = JINJA_ENVIRONMENT.get_template('templates/panel-pronosticos.html')
                    self.response.write(template.render(content))
                    return
        self.redirect('/')

class FichaPronostico(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.activo:
                    key = self.request.get('key')
                    jornada = Jornada.get(key)
                    pronostico_jornada =  PronosticoJornada.all()
                    pronostico_jornada.filter('jornada =', jornada)
                    pronostico_jornada.filter('usuario =', usuario)
                    pronostico_jornada = pronostico_jornada.get()

                    fecha_limite = jornada.fecha_inicio
                    if fecha_limite != None:
                        fecha_limite = fecha_limite - datetime.timedelta(hours=2)

                    result_dict = {}

                    if pronostico_jornada != None:
                        for pronostico_partido in pronostico_jornada.pronosticopartido_set:
                            result_dict[pronostico_partido.partido.key()] = {}
                            result_dict[pronostico_partido.partido.key()]['local'] = pronostico_partido.goles_local
                            result_dict[pronostico_partido.partido.key()]['visitante'] = pronostico_partido.goles_visitante
                    else:
                        pronostico_jornada = PronosticoJornada(usuario=usuario, jornada=jornada)
                        pronostico_jornada.put()

                    content = {'pronostico': pronostico_jornada, 'result_dict': result_dict, 'fecha_limite': fecha_limite, 'usuario': usuario}
                    template = JINJA_ENVIRONMENT.get_template('templates/pronostico.html')
                    self.response.write(template.render(content))
                    return
        self.redirect('/')

    def post(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.activo:
                    key = self.request.get('key')
                    pronostico_jornada = PronosticoJornada.get(key)
                    partido_key_set = []
                    for arg in self.request.arguments():
                        if arg != 'key' and arg.startswith('goles-local-'):
                            partido_key_set.append(arg.replace('goles-local-', ''))

                    for partido_key in partido_key_set:

                        goles_local = self.request.get('goles-local-%s' % partido_key)
                        goles_visitante = self.request.get('goles-visitante-%s' % partido_key)

                        if goles_local != '' and goles_visitante != '':

                            partido = Partido.get(partido_key)
                            pronostico_partido = PronosticoPartido.all()
                            pronostico_partido.filter("pronostico_jornada =", pronostico_jornada)
                            pronostico_partido.filter("partido =", partido)
                            pronostico_partido = pronostico_partido.get()

                            if pronostico_partido == None:
                                pronostico_partido = PronosticoPartido(pronostico_jornada=pronostico_jornada, partido=partido, goles_local=int(goles_local), goles_visitante=int(goles_visitante))
                                pronostico_partido.put()
                            else:
                                pronostico_partido.goles_local = int(goles_local)
                                pronostico_partido.goles_visitante = int(goles_visitante)
                                db.put(pronostico_partido)

                    self.redirect('/pronosticos')
                    return

        self.redirect('/')

class PronosticoGoleadores(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.activo:
                    jornada = Jornada.get(self.request.get('key'))

                    pronostico_jornada = PronosticoJornada.all()
                    pronostico_jornada.filter("jornada =", jornada)
                    pronostico_jornada.filter("usuario =", usuario)
                    pronostico_jornada = pronostico_jornada.get()

                    if pronostico_jornada == None:
                        pronostico_jornada = PronosticoJornada(jornada=jornada, usuario=usuario)
                        pronostico_jornada.put()

                    pronosticos_jugadores = PronosticoJugador.all()
                    pronosticos_jugadores.filter("pronostico_jornada =", pronostico_jornada)

                    defensas = Jugador.all()
                    defensas.filter("demarcacion =", 'Defensa')
                    defensas.order("nombre")
                    centrocampistas = Jugador.all()
                    centrocampistas.filter("demarcacion =", 'Centrocampista')
                    centrocampistas.order("nombre")
                    delanteros = Jugador.all()
                    delanteros.filter("demarcacion =", 'Delantero')
                    delanteros.order("nombre")
                    content = {'defensas': defensas, 'centrocampistas': centrocampistas, 'delanteros': delanteros, 'jornada': jornada, 'pronosticos_jugadores': pronosticos_jugadores, 'usuario': usuario}
                    template = JINJA_ENVIRONMENT.get_template('templates/pronostico-goleadores.html')
                    self.response.write(template.render(content))
                    return

        self.redirect('/')

    def post(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.activo:
                    jornada = Jornada.get(self.request.get('key'))

                    defensa_key = self.request.get('defensa')
                    centrocampista_key = self.request.get('centrocampista')
                    delantero_key = self.request.get('delantero')
                    defensa, centrocampista, delantero = None, None, None

                    if defensa_key != '':
                        defensa = Jugador.get(defensa_key)

                    if centrocampista_key != '':
                        centrocampista = Jugador.get(centrocampista_key)

                    if delantero_key != '':
                        delantero = Jugador.get(delantero_key)

                    pronostico_jornada = PronosticoJornada.all()
                    pronostico_jornada.filter("jornada =", jornada)
                    pronostico_jornada.filter("usuario =", usuario)
                    pronostico_jornada = pronostico_jornada.get()

                    for pronostico_jugador in pronostico_jornada.pronosticojugador_set:
                        db.delete(pronostico_jugador)

                    if defensa != None:
                        pronostico_jugador = PronosticoJugador(pronostico_jornada=pronostico_jornada, jugador=defensa)
                        pronostico_jugador.put()

                    if centrocampista != None:
                        pronostico_jugador = PronosticoJugador(pronostico_jornada=pronostico_jornada, jugador=centrocampista)
                        pronostico_jugador.put()

                    if delantero != None:
                        pronostico_jugador = PronosticoJugador(pronostico_jornada=pronostico_jornada, jugador=delantero)
                        pronostico_jugador.put()

                    self.redirect('/pronosticos')
                    return

        self.redirect('/')

class PronosticosGlobales(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.activo:
                    pronostico_global = PronosticoGlobal.all()
                    pronostico_global.filter("usuario =", usuario)
                    pronostico_global = pronostico_global.get()

                    if pronostico_global == None:
                        pronostico_global = PronosticoGlobal(usuario=usuario)
                        pronostico_global.put()

                    equipos_liga = Equipo.all()
                    equipos_liga.filter("lfp =", True)
                    equipos_liga.order("nombre")

                    equipos_champions = Equipo.all()
                    equipos_champions.filter("champions =", True)
                    equipos_champions.order("nombre")

                    equipos_uefa = Equipo.all()
                    equipos_uefa.filter("uefa =", True)
                    equipos_uefa.order("nombre")

                    porteros = Jugador.all()
                    porteros.filter("demarcacion =", 'Portero')
                    porteros.order("nombre")

                    content = {'pronostico_global': pronostico_global, 'equipos_liga': equipos_liga, 'equipos_champions': equipos_champions, 'equipos_uefa': equipos_uefa, 'porteros': porteros, 'usuario': usuario}
                    template = JINJA_ENVIRONMENT.get_template('templates/pronosticos-globales.html')
                    self.response.write(template.render(content))
                    return

        self.redirect('/')

# IMPORTANTE: COMENTAR ESTE METODO Y SU HANDLER
class CargarJornadas(webapp2.RequestHandler):
    def get(self):
        with open('datos/calendario.html') as f:
            local = None
            visitante = None
            num_partido = 1
            num_jornada = 1

            print 'Jornada %s' % num_jornada
            print '*' * 10

            jornada = Jornada(numero=num_jornada)
            jornada.put()

            for line in f:
                if num_jornada <= 19:
                    if 'local' in line:
                        partial_local = line[:line.rfind('</span>')]
                        local = partial_local[partial_local.rfind('>') + 1:]
                    elif 'visitante' in line:
                        partial_visitante = line[:line.rfind('</span>')]
                        visitante = partial_visitante[partial_visitante.rfind('>') + 1:]

                    if local != None and visitante != None:
                        print '%s - %s' % (local, visitante)
                        equipos = Equipo.all()
                        equipo_local = None
                        equipo_visitante = None
                        for equipo in equipos:
                            if equipo.nombre == local.decode('utf-8'):
                                equipo_local = equipo
                            elif equipo.nombre == visitante.decode('utf-8'):
                                equipo_visitante = equipo
                        if equipo_local == None:
                            print 'Creando equipo: %s' % local
                            equipo_local = Equipo(nombre=local.decode('utf-8'), lfp=True, champions=False, uefa=False)
                            equipo_local.put()
                        if equipo_visitante == None:
                            print 'Creando equipo: %s' % visitante
                            equipo_visitante = Equipo(nombre=visitante.decode('utf-8'), lfp=True, champions=False, uefa=False)
                            equipo_visitante.put()

                        partido = Partido(local=equipo_local, visitante=equipo_visitante, jornada=jornada)
                        partido.put()

                        equipo_local = None
                        equipo_visitante = None

                        local, visitante = None, None
                        if num_partido >= 10:
                            if num_jornada == 1:
                                time.sleep(10)
                            num_jornada += 1
                            num_partido = 1
                            print
                            print
                            if num_jornada <= 19:
                                print 'Jornada %s' % num_jornada
                                print '*' * 10
                                jornada = Jornada(numero=num_jornada)
                                jornada.put()
                        else:
                            num_partido += 1
                else:
                    break

            time.sleep(10)
            jornadas = Jornada.all()
            jornadas.order("numero")
            for jornada in jornadas:
                jornada_vuelta = Jornada(numero=num_jornada)
                jornada_vuelta.put()
                num_jornada += 1
                for partido in jornada.partido_set:
                    partido_vuelta = Partido(local=partido.visitante, visitante=partido.local, jornada=jornada_vuelta)
                    partido_vuelta.put()

class CargarJugadores(webapp2.RequestHandler):
    def get(self):
        parser = HTMLParser()
        for filename in os.listdir('datos/plantillas'):
            try:
                with open('datos/plantillas/%s' % filename) as f:

                    print filename

                    equipo = Equipo.all()
                    equipo = equipo.filter("nombre =", filename.replace('.html', '').decode('utf-8'))
                    equipo = equipo.get()

                    #print equipo.nombre
                    for line in f:
                        nombre_jugador = None
                        demarcacion = None

                        line = parser.unescape(line).encode('utf-8')
                        m = re.search('<p>(\\w| |ñ|á|é|í|ó|ú)*</p>', line , re.UNICODE | re.IGNORECASE)
                        if m != None:
                            nombre_jugador = m.group(0).replace('<p>', '').replace('</p>', '')

                        m = re.search('<p class="posicion">(\w| |á|é|í|ó|ú)*</p>', line, re.UNICODE | re.IGNORECASE)
                        if m != None:
                            demarcacion = m.group(0).replace('<p class="posicion">', '').replace('</p>', '')

                        if nombre_jugador != None and demarcacion != None:
                            #print nombre_jugador, equipo.nombre.encode('utf-8')
                            if demarcacion == 'Medio':
                                demarcacion = 'Centrocampista'
                            #print nombre_jugador, demarcacion
                            print nombre_jugador
                            jugador = Jugador(nombre=nombre_jugador.decode('utf-8'), demarcacion=demarcacion, equipo=equipo)
                            jugador.put()
            except Exception as e:
                print e
                break


app = webapp2.WSGIApplication([
    ('/cargarjugadores', CargarJugadores),
    ('/cargarjornadas', CargarJornadas),
    ('/pronostico-global', PronosticosGlobales),
    ('/pronosticos/goleadores', PronosticoGoleadores),
    ('/pronosticos/nuevo', FichaPronostico),
    ('/pronosticos', Pronosticos),
    ('/admin/usuarios/nuevo', FichaUsuario),
    ('/admin/usuarios', Usuarios),
    ('/admin/jornadas/goleadores/borrar', BorrarGoleador),
    ('/admin/jornadas/goleadores/nuevo', FichaGoleador),
    ('/admin/jornadas/goleadores', Goleadores),
    ('/admin/jornadas/borrar', BorrarJornada),
    ('/admin/jornadas/nuevo', FichaJornada),
    ('/admin/jornadas', Jornadas),
    ('/admin/jugadores/borrar', BorrarJugador),
    ('/admin/jugadores/nuevo', FichaJugador),
    ('/admin/jugadores', Jugadores),
    ('/admin/equipos/borrar', BorrarEquipo),
    ('/admin/equipos/nuevo', FichaEquipo),
    ('/admin/equipos', Equipos),
    ('/admin', Admin),
    ('/', MainHandler)
], debug=True)
