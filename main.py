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
from model import Usuario, Equipo, Jugador, Jornada, Partido
from google.appengine.ext import db

import webapp2
import jinja2
import os
import time

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

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
                content = {'nick': usuario.nick, 'email': usuario.email}
                self.response.write(template.render(content))
                return 
                
            content = {}
            if usuario.admin:
                print usuario.admin
                content['admin'] = True
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
                    self.response.write(template.render())
                    return 
        self.redirect('/')

class Jugadores(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            usuario = Usuario.gql("WHERE user_id = '%s'" % user.user_id()).get()
            if usuario != None:
                if usuario.admin:
                    jugadores = Jugador.all()
                    jugadores_list = []
                    for jugador in jugadores:
                        jugadores_list.append(jugador)
                    content = {'jugadores': jugadores_list}
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
                    content = {}
                    equipos = Equipo.all()
                    equipos_list = []
                    for equipo in equipos:
                        equipos_list.append(equipo)
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
                    equipos = Equipo.all()
                    equipos_list = []
                    for equipo in equipos:
                        equipos_list.append(equipo)
                    content = {'equipos': equipos_list}
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
                        content = {'equipo': equipo}
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
                            print dir(partido) 
                        jornada_list.append(jornada)
                    content = {'jornadas': jornada_list}
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
                    if key != '':
                        jornada = Jornada.get(key)
                        partidos = jornada.partido_set
                        partidos_list = []
                        equipos = Equipo.all()
                        equipos.filter("lfp =", True)
                        for partido in partidos:
                            partidos_list.append(partido)
                        content = {'jornada': jornada, 'partidos': partidos_list, 'equipos': equipos}
                        self.response.write(template.render(content))
                    else:
                        content = {'rango': range(10), 'equipos': equipos}
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



app = webapp2.WSGIApplication([
    ('/cargarjornadas', CargarJornadas),
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
