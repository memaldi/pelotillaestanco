#!/usr/bin/env python
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
from model import Usuario, Equipo
from google.appengine.ext import db

import webapp2
import jinja2
import os

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
                        print equipo.key()
                        equipos_list.append(equipo)
                    content = {'equipos': equipos_list}
                    template = JINJA_ENVIRONMENT.get_template('templates/panel-equipos.html')
                    self.response.write(template.render(content))
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

app = webapp2.WSGIApplication([
    ('/admin/equipos/nuevo', FichaEquipo),
    ('/admin/equipos', Equipos),
    ('/admin', Admin),
    ('/', MainHandler)
], debug=True)
