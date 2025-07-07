#!/usr/bin/python
import sys, os, json
import cgi
from display.displctrl import *

class Modctrl:
    def __init__(self):
        self.dspl = Displayctrl()
        self.request_method = os.environ['REQUEST_METHOD']
        self.request_uri = str(os.environ['REQUEST_URI']).split("/")[1:]
        self.current_mod = "" if len(self.request_uri) <= 1 else self.request_uri[1]
        self.pwd = os.getcwd()
        self.moddir = os.path.join(self.pwd,"modules")
        self.mods ={'': {"name" : "Home", "uri" : "", "anchors" : ["permission"] , "menu" : [], "tittle" : ""}}
        self.root_html="/".join(["http:/",os.environ['HTTP_HOST'],"admin_rancid"])


    def list_mod(self):
        mod_dir = [os.path.join(self.moddir,o) for o in os.listdir(self.moddir) if os.path.isdir(os.path.join(self.moddir,o))]
        for dir in mod_dir:
            try:
                with open(os.path.join(dir,"mod.json"),'r') as mod:
                    module = json.loads(mod.read())
                module['dir'] = dir
                if self.mod_is_anchor("permission"):
                    self.mod_anchor("permision",self)
                else:
                    self.mods[module['uri']]=module
            except:
                pass
        menu2 = []
        cont_menu2 = 0
        curr_menu2 = 0
        for i in self.mods:
            menu2.append([self.mods[i]['name'], "/admin_rancid/" + self.mods[i]['uri']])
            curr_menu2 = cont_menu2 if self.mods[i]['uri'] == self.current_mod else curr_menu2
            cont_menu2 += 1
        self.dspl.set_menu_2(menu2,curr_menu2)

    def run_mod(self):
        if self.current_mod != "":
            if len(self.request_uri) >= 3:
                mod_file = self.mods[self.current_mod]['run'].get(self.request_uri[2], self.mods[self.current_mod]['run']['default'])
            else:
                mod_file = self.mods[self.current_mod]['run']['default']
            _temp = __import__('modules' + '.' + os.path.basename(self.mods[self.current_mod]['dir']) + '.' + mod_file, globals(), locals(), ['main'], -1)
            mod = _temp.main
            tomod = {'dspl' : self.dspl, 'uri' : self.request_uri, 'pwd' : self.pwd, 'moddir' : self.moddir, 'modinfo' : self.mods[self.current_mod], 'root_html' : self.root_html}
            module = mod(tomod)
            if self.request_method == "GET":
                module.get()
            elif self.request_method == "POST":
                cgi_form = cgi.FieldStorage()
                form = {}
                for item in cgi_form:
                    form[item] = cgi_form.getvalue(item)
                module.post(form)
        else:
            print(f"Location: {self.root_html}/rancid")
    def check_mod(self):
        pass
    def install_mod(self):
        pass
    def main_mod(self):
        pass
    def mod_anchor(self,anchor,mod):
        pass
    def mod_is_anchor(self,anchor):
        return False
    def mod_frame(self):
        pass
    def run(self):
        # configuracion listado de menu
        self.list_mod()
        with open('web.json','r') as json_read:
            self.web=json.loads(json_read.read())
        # cabeceras y archivos de estilo
        self.dspl.set_head(self.web['tittle'] , self.web['keywords'] , self.web['comment'] , self.web['icon'], self.web['style'])
        self.dspl.set_tittle(self.web['logo'],self.web['message'])
        # presentacion de informacion segun modulo
        try:
            self.dspl.set_menu_1('MENU', self.mods[self.current_mod]['menu'])
        except:
            print(f'Location: {self.root_html}')
        self.dspl.append_content('mod_tittle','tittle',self.mods[self.current_mod]['tittle'])
        self.run_mod()
        print("Content-Type: text/html\r\n")
        print("\r\n")
        # salida html
        print(os.environ.get('REMOTE_USER',"NO USER"))
        print(self.dspl.get_full_html())
