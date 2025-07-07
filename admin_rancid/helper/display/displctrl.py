#!/usr/bin/python
import os
class Displayctrl:
    def __init__(self):
        self.head='<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'
        self.tittle=''
        self.menu_1=''
        self.menu_2=''
        self.content={}
        self.content['skel']={'type' : 'main', 'content' : []}
        self.content['dict']={'main':self.content['skel']}
        self.content['current'] = self.content['skel']
        self.content['html']=""
        self.footer=''
        self.content_type="Content-Type: text/html"

    def set_head(self,tittle,keywords,desc,icon,css):
        """ configuracion de cabeceras html """
        self.head += "<title>" + tittle + "</title>"
        tmp = ''
        for i in keywords:
            tmp +=  i if tmp == '' else ', ' + i
        self.head += '' if tmp == '' else '<meta name="keywords" content="' + tmp + '" />'
        self.head += '<meta name="description" content="' + desc + '" />'
        self.head += '<link rel="icon" type="image/png" href="' + icon + '">'
        for i in css:
            self.head += '<link href="' + i + '" rel="stylesheet" type="text/css" />'

    def append_head(self, txt):
        self.head += txt

    def html_redirect(self,url):
        self.append_head('<meta http-equiv="Refresh" content="0; url=' + url + '">')

    def set_tittle(self, logo, msj):
        self.tittle = '<h1><a href="/admin_rancid/" target="_parent">'
        self.tittle += '<img src="' + logo + '" alt="CSS Templates" />'
        self.tittle += '<span>' + msj + '</span></a></h1>'

    def set_menu_1(self, tittle, items):
        self.menu_1 = '' if tittle == '' else '<h2>' + tittle + '</h2>'
        self.menu_1 += '<ul class="service_list">'
        for i in items:
            self.menu_1 += '<li><a href="' + i[1] + '">' + i[0] + '</a></li>'
        self.menu_1 += '</ul>'

    def set_menu_2(self,items , current):
        self.menu_2 = '<ul>'
        for i in range(len(items)):
            self.menu_2 += '<li><a href="' + items[i][1] + '" target="_parent" ' + ( '' if current != i else 'class="current"') + '>' + items[i][0] + '</a></li>'
        self.menu_2 += '</ul>'

    def build_content(self,item,html=''):
        'creador de contenido, [0] tipo y [1] contenido'
        html_b = html
        html_func = {
            'text' : lambda x : str(x['content']),
            'newline' : lambda x : '<br/>',
            'line' : lambda x : '<hr/>',
            'paragraph' : lambda x : "<p>" + self.build_content(x['content']) + "</p>",
            'tittle' : lambda x: "<h2>" + str(x['content']) + "</h2>",
            'main' : lambda x: self.build_content(x['content']),
            'list' : lambda x: '<ul>' + self.build_content(x['content']) + '</ul>',
            'list_item' : lambda x: '<li>' + self.build_content(x['content']) + '</li>',
            'fieldset' : lambda x: '<fieldset> <legend>' + x['legend'] + '</legend>' + self.build_content(x['content']) + '</fieldset>',
            'table' : lambda x: '<table>' + self.build_content(x['content']) + '</table>',
            'table_row' : lambda x: '<tr>' +  self.build_content(x['content']) + '</tr>',
            'table_data' : lambda x: '<td>' + self.build_content(x['content']) + '</td>',
            'table_head' : lambda x: '<th>' + self.build_content(x['content']) + '</th>',
            'table_solid_data' : lambda x: '<td style="border-width:1px;border-style:solid;border-color:black;border-collapse:collapse;border-spacing:0">' + self.build_content(x['content']) + '</td>',
            'table_solid_head' : lambda x: '<th style="border-width:1px;border-style:solid;border-color:black;border-collapse:collapse;border-spacing:0">' + self.build_content(x['content']) + '</th>',
            'form' : lambda x: '<form action="' + x['action'] + '" method="post">' + self.build_content(x['content']) + '</form>' ,
            'form-id' : lambda x: '<form action="' + x['action'] + '" method="post" id="' + x['id'] + '">' + self.build_content(x['content']) + '</form>' ,
            'form-disable' : lambda x: '<form action="' + x['action'] + '" method="post" onsubmit="document.getElementsByName(\'submit_value\')[0].disabled=true; return true;">' + self.build_content(x['content']) + '</form>' ,
            'form-disable-org' : lambda x: '<form action="' + x['action'] + '" method="post" onsubmit="document.getElementsByName(\'submit_value\').forEach( x => x.disabled=true); return true;">' + self.build_content(x['content']) + '</form>' ,
            'form-disable-id' : lambda x: '<form action="' + x['action'] + '" method="post" onsubmit="document.getElementById(\'submit_value\').disabled=true; return true;">' + self.build_content(x['content']) + '</form>' ,
            'link' : lambda x: '<a href="' + x['href'] + '">' + str(x['content']) + '</a>' ,
            'link_blank' : lambda x: '<a href="' + x['href'] + '" target="_blank">' + str(x['content']) + '</a>' ,
            'submit' : lambda x: '<input type="submit" name="submit_value" value="' + str(x['content']) + '"/>',
            'submit-id--' : lambda x: '<input type="submit" id="' + x['id'] + '" name="submit_value" value="' + str(x['content']) + '"/>',
            'submit-id' : lambda x: '<input type="submit" id="submit_value" name="submit_value" value="' + str(x['content']) + '"/>',
            'button-onclick' : lambda x: '<button type="button" onclick="' + x['onclick'] + '">' + str(x['content']) + '</button>',
            'hidden' : lambda x: '<input type="hidden" name="' + str(x['name']) + '" value="' + str(x['value']) + '"/>',
            'hidden-id' : lambda x: '<input type="hidden" name="' + str(x['name']) + '" value="' + str(x['value']) + '" id="' + x['id']+ '"/>',
            'radio' : lambda x: '<label><input type="radio" name="' + x['name'] + '" value="' + x['value'] + '"/>' + str(x['content']) + '</label><br/>',
            'check' : lambda x: '<label><input type="checkbox" name="' + x['name'] + '" value="' + x['value'] + '"/>' + str(x['content']) + '</label><br>',
            'password' : lambda x: '<label>' + str(x['content']) + '</label><br/><input type="password" name="' + x['name'] + '" value="' + x['value'] + '"/><br/>',
            'textarea' : lambda x: '<label>' + str(x['content']) + '</label><br/><textarea  rows="10" cols="71" name="' + x['name'] + '"></textarea><br/>',
            'textarea_output' : lambda x: '<label></label><br/><textarea  rows="10" cols="71" name="' + x['name'] + '">' + str(x['content']) + '</textarea><br/>',
            'input' : lambda x: '<label>' + str(x['content']) + '</label><br/><input type="text" name="' + x['name'] + '" value="' + x['value'] + '"/><br/>'
            }
        if self.content['html'] != "":
            html_b += self.content['html']
        else:
            for x in item:
                html_b += html_func.get(x['type'], lambda x: '<' + x['type'] + '>' + str(x['content']) + '</' + x['type'] + '>')(x)
        return html_b

    def set_content(self, html_content):
        self.content['html'] = html_content
    def add_content(self,id,type, content=None, options=None):
        if content is None:
            content=[]
        if options is None:
            options={}
        self.content['dict'][id]={'type' : type, 'content' : content}
        self.content['dict'][id].update(options)
        self.content['current']['content'].append(self.content['dict'][id])
        self.content['current'] = self.content['dict'][id]

    def append_content(self,id,type, content=None, options=None):
        if content is None:
            content=[]
        if options is None:
            options={}
        self.content['dict'][id]={'type' : type, 'content' : content}
        self.content['dict'][id].update(options)
        self.content['current']['content'].append(self.content['dict'][id])

    def insert_content(self,parent,id,type,content=None,options=None):
        if content is None:
            content=[]
        if options is None:
            options={}
        self.content['dict'][id]={'type' : type, 'content' : content}
        self.content['dict'][id].update(options)
        self.content['dict'][parent]['content'].append(self.content['dict'][id])

    def set_content_current(self,id):
        self.content['current'] = self.content['dict'][id]

    def append_content_input(self,id,type,name,value="",content=""):
        self.append_content(id,type, content, options={'value' : value, 'name' : name})

    def set_footer(self):
        with open('display/footer.html','r') as html:
            self.footer=html.read()

    def get_full_html(self):
        html_content = self.build_content(self.content['dict']['main']['content'])
        print(self.content_type)
        print("\r\n\r\n")
        with open('display/skel.html','r') as html:
            full_html=html.read()
        full_html=full_html.replace('%%head%%', self.head)
        full_html=full_html.replace('%%tittle%%', self.tittle)
        full_html=full_html.replace('%%menu_1%%', self.menu_1)
        full_html=full_html.replace('%%menu_2%%', self.menu_2)
        full_html=full_html.replace('%%content%%', str(html_content))
        #full_html=full_html.replace('%%footer%%', self.footer)
        return full_html