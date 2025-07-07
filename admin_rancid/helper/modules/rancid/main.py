import cgi , json, pexpect, os, time, sys, datetime, shlex, re, io, re, subprocess
import expect_base as exp
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from dotenv import load_dotenv
import os

load_dotenv()          
db_user = os.environ["DB_USER"]
db_pass = os.environ["DB_PASS"]
db_host = os.environ["DB_HOST"]
db_name = os.environ["DB_NAME"]
ruckus_user = os.environ["RUCKUS_USER"]
ruckus_pass = os.environ["RUCKUS_PASS"]
applications_user = os.environ["APPLICATIONS_USER"]
applications_pass = os.environ["APPLICATIONS_PASS"]
applications_host = os.environ["APPLICATIONS_HOST"]
applications_name = os.environ["APPLICATIONS_NAME"]
ruckus_register_pass = os.environ["RUCKUS_REGISTER_PASS"]
ruckus_register_user = os.environ["RUCKUS_REGISTER_USER"]
ruckus_register_port = os.environ["RUCKUS_REGISTER_PORT"]
csc_user = os.environ["CSC_USER"]
csc_pass = os.environ["CSC_PASS"]

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
LOG_DIR = os.path.join(SCRIPT_DIR, 'logs')
if not os.path.isdir(LOG_DIR):
    try:
        os.makedirs(LOG_DIR)
    except Exception:
        pass

LOG_PATH = os.path.join(LOG_DIR, 'ip2_debug.log')

def is_valid_ipv4(addr):
	parts = addr.split('.')
	if len(parts) != 4:
		return False
	for p in parts:
		if not p.isdigit():
			return False
		i = int(p)
		if (i < 0) or (i > 255):
			return False
	return True

class main:
    def __init__(self,ctr_data):
        self.ctr_data = ctr_data
        self.dspl=ctr_data['dspl']
        self.uri=ctr_data['uri']
        self.scripts={}
        if len(self.uri) > 2:
            self.curr_script = self.uri[2]
        else:
            self.curr_script = ""
        self.form={}
        scripts = [['IPS', 'ips'], ['RESUMEN', 'resumen'], ['RESPALDOS', 'respaldos'] , ['INGRESO', 'ingreso']]
        self.dspl.set_menu_1('MENU', [[i[0], "/admin_rancid/" + self.uri[1] + "/" + i[1] ] for i in scripts]+[["ELIMINAR","/eliminar\" target=\"_blank\""],["AUDITORIA","/auditoria\" target=\"_blank\""]])

    def list_customers(self):
        d = []
        #with io.open("/var/www/html/admin_rancid/archivos_pruebas/hosts",'r', encoding='UTF-8') as file:
        #    file_contet = file.readlines()
        #for line in file_contet:
        #    if "####" in line:
        #        if len(line) > 6:
        #            l_encode = line.replace("\t"," ").replace("#### ","").rstrip()
        #            d += [l_encode]
        d = [ d for d in os.listdir('/usr/local/rancid/var') if os.path.join('/usr/local/rancid/var', d)]
        return d

    def new_informacion_sede_cliente(self,insert_to, form=None):
        if form is None:
            form = {'cliente': "", 'maximo' : "", 'pais' : "", 'ciudad' : "", 'sede' : ""}
        d = self.list_customers()
        lista = '<label>CLIENTE:</label></br><input list="clientes" name="cliente" value="' + form['cliente'] + '"></br><datalist id="clientes">'
        for customer in d:
            lista +='<option value="' + customer + '">'
        lista +='</datalist>'

        paises = sorted(["","GT","HN","CO","CR","DR","PA","PR","EC","PE","SV","NI","EC","US","MX","AG","AI","BB","BM","BS","DM","GD","GP","JM","KN","KY","LC","MQ","MS","TC","TT","VC","VG","VI","LC","CW","CU","CH","CL"])
        option_pais = ""
        for i in paises:
            option_pais+='<option value="' + i + '" ' + ('selected="selected"' if form['pais']== i else '' ) + '>' + i + '</option>'

        self.dspl.insert_content(insert_to, 'fieldset','fieldset',[],{ 'legend' : 'INFORMACION CLIENTE Y SEDE'})
        self.dspl.insert_content('fieldset','input_cliente','span',lista)
        #self.dspl.insert_content('fieldset','input_cliente_maximo','input','CLIENTE MAXIMO:',{'value' : form['maximo'], 'name' : 'maximo'})
        self.dspl.insert_content('fieldset','input_cliente_maximo','input','CLIENTE RESUMEN:',{'value' : form['maximo'], 'name' : 'maximo'})
        #self.dspl.insert_content('fieldset','input_pais','input','SIGLAS PAIS (ej: CO, CR, PR...):',{'value' : form['pais'], 'name' : 'pais'})
        self.dspl.insert_content('fieldset','input_equipo','span','<label>SIGLAS PAIS:</label></br><select  name="pais">' + option_pais + '</select></br>')
        self.dspl.insert_content('fieldset','input_ciudad','input','CIUDAD:',{'value' : form['ciudad'], 'name' : 'ciudad'})
        self.dspl.insert_content('fieldset','input_sede','input','NOMBRE SEDE:',{'value' : form['sede'], 'name' : 'sede'})

    def new_informacion_servicio(self, insert_to, switch=None, form=None):
        if switch is None:
            switch = 'router'
        if form is None:
            form = {'id' : "", 'id_rel' : '', 'funcion' : '' }
        self.dspl.insert_content(insert_to, 'fieldset','fieldset',[],{ 'legend' : 'INFORMACION SERVICIO'})
        self.dspl.insert_content('fieldset','input_sede','input','ID EQUIPO:',{'value' : form['id'], 'name' : 'id'})
        self.dspl.insert_content('fieldset','input_sede','input','IDs RELACIONADOS:',{'value' : form['id_rel'], 'name' : 'id_rel'})
        self.dspl.insert_content('fieldset','input_sede','input','ID:',{'value' : form['funcion'], 'name' : 'funcion'})


    def new_informacion_equipo(self, insert_to, switch=None, form=None):
        if form is None:
            form = { 'ip' : '' , 'marca' : '' , 'red' : '' , 'ip_2': '', 'relation_cid': '', 'relation_type': ''}
        if switch is None:
            switch = 'router'

        self.dspl.insert_content(insert_to, 'fieldset','fieldset',[],{ 'legend' : 'INFORMACION EQUIPO'})
        if switch == 'firewall':
            tipos = [['DCN', 'GFW_FIREWALL'], ['Internet','FW_FIREWALL']]
            option_tipos = ''
            for i in tipos:
                option_tipos += '<option value="' + i[1] + '" ' + ( ' selected="selected"' if form['red'] == i[1] else '' ) + '>' + i[0] + '</options>'
            self.dspl.insert_content('fieldset', 'input_equipo','span','<label>RED TOMA DE BK:</label></br><select  id="red" name="red"></br>' + option_tipos + '</select></br>')
            equipos = [['FORTIGATE','FORTIGATE'], ["VERSA-FX", "VERSA-FX"]]
        elif switch == 'traficmanager':
            equipos = [['exinda','exinda'],['exinda1','exinda1'],['exinda2','exinda2']]
        elif switch == 'wifi':
            equipos = [['ruckus-zd','ruckus-zd'],['ruckus-sz','ruckus-sz'],['cisco-wlc5','cisco-wlc5']]
        elif switch == 'audiocodes':
            equipos = [['audio-codes','audio-codes']]
        else:
            equipos = [['CISCO','CISCO'],['JUNIPER','JUNIPER'],['CISCO-SGXXX', 'SGXXX'],['FORTIGATE','FORTIGATE'], ["VERSA-FX", "VERSA-FX"]]
        option_equipos=''
        for i in equipos:
            option_equipos+='<option value="' + i[0] + '" ' + ('selected="selected"' if form['marca']== i[0] else '') + '>' + i[1] + '</option>'

        self.dspl.insert_content('fieldset','input_equipo','span','<label>MARCA EQUIPO:</label></br><select  id="marca" name="marca"></br>' + option_equipos + '</select></br>')
        self.dspl.insert_content('fieldset','input_ip','input','IP:',{'value' : form['ip'], 'name' : 'ip'})
        
        if switch in ('router','firewall'):
            self.dspl.insert_content('fieldset','fs_redund','fieldset',[],{'legend': 'INFORMACION REDUNDANCIA'})
            self.dspl.insert_content('fs_redund','input_ip2','input','IP DCN2:', {'value': form.get('ip_2',''), 'name': 'ip_2'})
            self.dspl.insert_content('fs_redund','input_rel_cid','input','CID relacionado:',{'value': form.get('relation_cid',''), 'name': 'relation_cid'})
            opts = ['<option value="">--</option>']
            for lbl, val in [('Working','WORKING'), ('Protection','PROTECTION')]:
                sel = ' selected' if form.get('relation_type')==val else ''
                opts.append('<option value="%s"%s>%s</option>' % (val,sel,lbl))
            self.dspl.insert_content('fs_redund','input_rel_type','span','<label>Tipo de redundancia:</label><br>''<select name="relation_type">%s</select><br>' % ''.join(opts))

#    def new_firewall(self, insert_to, dev=None, form=None):
#        if form is None:
#            form = {"red" : "", 'ip' : '', 'name' : ''}
#        if dev != 'firewall':
#            return
#        tipos = [['DCN', 'GFW_FIREWALL'], ['Internet','FW_FIREWALL']]
#        option_tipos = ''
#        for i in tipos:
#            option_tipos += '<option value="' + i[1] + '" ' + ( ' selected="selected"' if form['red'] == i[1] else '' ) + '>' + i[0] + '</options>'
#        self.dspl.insert_content(insert_to, 'fieldset', 'fieldset' , [], {'legend' : 'FIREWALL'})
#        self.dspl.insert_content('fieldset', 'input_equipo','span','<label>RED TOMA DE BK:</label></br><select  id="red" name="red"></br>' + option_tipos + '</select></br>')
#        self.dspl.insert_content('fieldset','input_hostname','input','HOSTNAME:',{'value' : form['name'], 'name' : 'name'})
#        self.dspl.insert_content('fieldset','input_ip','input','IP:',{'value' : form['ip'], 'name' : 'ip'})

    def form_validate(self, form):
        validation_error = False
        errors = []
        #cliente sede
        if 'cliente' not in form:
            form['cliente'] = ""
            validation_error |= True
            errors.append("cliente: Sin datos")
        if 'pais' not in form:
            form['pais'] = ""
            validation_error |= True
            errors.append("pais: Sin datos")
        if 'ciudad' not in form:
            form['ciudad'] = ""
            validation_error |= True
            errors.append("ciudad: Sin datos")
        if 'sede' not in form:
            form['sede'] = ""
            validation_error |= True
            errors.append("sede: Sin datos")

        form['cliente'] = form['cliente'].upper().rstrip().replace(" ", "_")
        form['pais'] = form['pais'].upper().rstrip()
        form['ciudad'] = form['ciudad'].rstrip().upper().replace(" ", "_")
        form['sede'] = form['sede'].rstrip().upper().replace(" ", "_")

        #servicio
        if 'id' not in form:
            form['id'] = ""
            validation_error |= True
            errors.append("ID: Sin datos")
        if 'id_rel' not in form:
            form['id_rel'] = ""
            #validation_error |= True
            #errors.append("ID Relacionados: Sin datos")

        form['id_sccd'] = form['id']
        form['id'] = form['id'].upper().rstrip().replace(".","").replace(" ","").replace("-","")
        form['id_rel'] = form['id_rel'].upper().rstrip().replace(".","").replace(" ","_").replace("-","")

        #equipo
        if form['dispositivo'] == 'firewall':
            if 'red' not in form:
                form['red'] = ""
                validation_error |= True
                errors.append("red toma de respaldo: Sin datos")

            form['red'] = form['red'].upper().rstrip()
            if re.search(r"^(FW_FIREWALL)|(GFW_FIREWALL)$", form['red']) is None:
                validation_error |= True
                errors.append("red toma de respaldos: Sin datos validos")
        if 'funcion' not in form:
            form['funcion'] = ""
            #validation_error |= True
            #errors.append("id: Sin datos")
        if 'maximo' not in form:
            form['maximo'] = ""
            validation_error |= True
            errors.append("cliente maximo: sin datos")

        form['maximo'] = form['maximo'].upper().rstrip().replace(".","").replace(" ","_")

        if re.search(r"^[A-Z0-9\s_]+$", form['cliente']) is None:
            validation_error |= True
            errors.append("cliente: Sin datos validos")
        #if re.search(r"^[A-Z]{1,2}$", form['pais']) is None:
        if re.search(r"^(CL)|(GT)|(HN)|(CO)|(CR)|(DR)|(PA)|(PR)|(EC)|(PE)|(SV)|(NI)|(EC)|(US)|(MX)|(AG)|(AI)|(BB)|(BM)|(BS)|(DM)|(GD)|(GP)|(JM)|(KN)|(KY)|(LC)|(MQ)|(MS)|(TC)|(TT)|(VC)|(VG)|(VI)|(LC)|(CW)|(CU)|(CH)$", form['pais']) is None:
            validation_error |= True
            errors.append("pais: Sin datos validos")
        if re.search(r"^[A-Z_]+$", form['ciudad']) is None:
            validation_error |= True
            errors.append("ciudad: Sin datos validos")
        if re.search(r"^[A-Z0-9_]+$", form['sede']) is None:
            validation_error |= True
            errors.append("sede: Sin datos validos")
        if re.search(r"^[0-9]{1,12}[A-Z]{1,3}$", form['id']) is None:
            validation_error |= True
            errors.append("CID: Sin datos validos")
        if form['id_rel'] != "":
            if re.search( r"^([0-9A-Z]{1,15}\s?_?)+$", form['id_rel']) is None:
                validation_error |= True
                errors.append("CID relacionados: Sin datos validos")
        if form['funcion'] != "":
            if re.search("^[0-9]{2}$", form['funcion']) is None:
                validation_error |= True
                errors.append("ID: Sin datos validos")

        if re.search(r"^[A-Z0-9\-_]+$", form['maximo']) is None:
            validation_error |= True
            errors.append("cliente maximo: datos invalidos")


        if 'ip' not in form:
            form['ip'] = ""
            validation_error |= True
            errors.append("ip: Sin datos")
        form['ip'] = form['ip'].upper().rstrip()
        if not is_valid_ipv4(form['ip']):
            validation_error = True
            errors.append("IP: Sin datos validos")


        with open("/etc/hosts","r") as f:
            hosts_lines = f.read().splitlines()

        if form['ip'] != "":
            for line in hosts_lines:
                if form['ip']+"\t" in line:
                    validation_error |= True
                    errors.append("IP: ip duplicada")
        if  form["id"] != "":
            for line in hosts_lines:
                if form["id"].lower() in line.lower():
                    validation_error |= True
                    errors.append("CID: duplicado")


        if os.system('ip address | grep -c 172.18.93.254 > /dev/null 2>&1') != 0:
            validation_error |= True
            errors.append("Estas en el servidor BK, por favor realizar desde el PPAL")

        engine = create_engine(f"mysql+mysqldb://{db_user}:{db_pass}@{db_host}/{db_name}")
        conn = engine.connect()
        ip2 = form.get('ip_2', '').strip()
        rel = form.get('relation_cid', '').strip()
        typ = form.get('relation_type', '').strip()
        if ip2:
            if (rel or typ):
                validation_error = True
                errors.append("No mezclar IP DCN2 con relacion de dispositivo")

            count_ip2 = conn.execute(
                text("SELECT COUNT(*) FROM net_inventory__devices WHERE ip_2 = :ip2"),
                ip2=ip2
            ).fetchone()[0]
            if count_ip2 > 0:
                validation_error = True
                errors.append("IP DCN2: ya existe en inventario")
        else:
            count = conn.execute(
                    text("SELECT COUNT(*) FROM net_inventory__devices WHERE cid_mgt = :cid"),
                    cid=rel
                ).fetchone()[0]
            already_relation_count = conn.execute(
                text("SELECT COUNT(*) FROM net_inventory__devices WHERE relation = :cid"),
                cid=rel
            ).fetchone()[0]
            if (rel or typ):
                if not (rel and typ):
                    validation_error = True
                    errors.append("Relacion: debe especificar CID y Tipo simultaneamente")
                elif rel == form.get('id', '').strip():
                    validation_error = True
                    errors.append("CID relacionado: no puede ser el mismo que el dispositivo")
                elif count == 0:
                    validation_error = True
                    errors.append("CID relacionado: no existe en inventario")
                elif already_relation_count > 0:
                    validation_error = True
                    errors.append("CID relacionado: Ya se ha registrado como relacion en otro equipo")
        conn.close()
 	    
        if form.get('dispositivo') in ('router','firewall'):
            form['ip_2'] = form.get('ip_2','').strip()
            if form['ip_2'] and not is_valid_ipv4(form['ip_2']):
                validation_error = True
                errors.append("IP DCN2: Sin datos validos")

        self.dspl.append_content('pre','p',", <br/>".join(errors))
        return validation_error

    def preproces(self, form):
        hostname = []
        clientes = self.list_customers()
        if form['cliente'] in clientes:
            form['isnew'] = False
        else:
            form['isnew'] = True
        hostname = [form['maximo'].replace(" ","_"),form['pais'],form['ciudad'],form['sede']]

        if form['funcion'] != "" :
            hostname += [form['funcion']]

        hostname += [form['id']]

        if form['id_rel'] != "":
            hostname += [form['id_rel']]

        if form['dispositivo'] == 'router':
            hostname = ["RTR"] + hostname
        elif form['dispositivo'] == 'stack':
            hostname = ["STACK"] + hostname
        elif form['dispositivo'] == 'traficmanager':
            hostname = ["TM"] + hostname
        elif form['dispositivo'] == 'firewall':
            hostname = [form['red']] + hostname
        elif form['dispositivo'] == 'wifi':
            hostname = ["WIFI"] + hostname
        elif form['dispositivo'] == 'audiocodes':
            hostname = ["AC"] + hostname
        else:
            hostname = ["SW"] + hostname
        form['hostname'] = "_".join(hostname)

        return form

    def cambiar_conf(self,form):
        if form['marca'] == "JUNIPER":
            script = f"""
            configure
            set system login user {applications_user} authentication plain-text-password
            {applications_pass}
            {applications_pass}
            set system root-authentication plain-text-password
            {applications_pass}
            {applications_pass}
            set system login retry-options tries-before-disconnect 4
            set system login retry-options lockout-period 2
            set system login class super-user-local idle-timeout 5
            set system login class super-user-local permissions all
            set system login user {applications_user} class super-user-local
            delete system login user csc
            commit
            exit
            """
        elif form['marca'] == 'CISCO':
            script = f"""
            config terminal
            username {applications_user} privilege 15 secret 0 {applications_pass}
            no username csc
            no banner login
            """
        elif form['marca'] == 'CISCO-SGXXX':
            script = ""
        else:
            script = ""

        child = exp.BaseExpect.start_ssh(csc_user,form['ip'])
        try:
            i = exp.BaseExpect.login_1(child,csc_user,csc_pass)
            if i != 0:
                exp.BaseExpect.script(child, i, script)
        except:
            self.dspl.insert_content('main','test','pre',"Unexpected error:" + str(sys.exc_info()))
            i=0
        child.close()
        self.dspl.append_content('fieldset','fieldset',[],{'legend':"OUTPUT"})
        self.dspl.insert_content('fieldset','output','pre',str(child.logfile.read()))
        return i

    def edit_hosts(self,new_device):
        with io.open("/etc/hosts",'r', encoding='UTF-8') as file:
            file_content = file.read()
        if new_device['isnew'] == True:
            file_content +="\n####"
            file_content +="\n#### " + new_device['cliente'].replace(' ','_')
            file_content +="\n####"
            file_content +="\n"+ new_device['ip'] + "\t" + new_device['hostname'] + "\n"
        else:
            temp = ""
            is_customer = False
            for line in file_content.splitlines():
                cliente=""
                if "####" in line:
                    temp1 = line.replace("\t"," ")
                    cliente = shlex.split(temp1)
                    if len(cliente) < 2:
                        cliente = ""
                    else:
                        cliente = " ".join(cliente[1:])
                    if new_device['cliente'] == cliente:
                        is_customer = True
                elif is_customer and "####" not in line:
                    is_customer = False
                    temp += new_device['ip'] + "\t" + new_device['hostname'] + "\n"
                temp += line + "\n"
            if is_customer:
                temp += new_device['ip'] + "\t" + new_device['hostname'] + "\n"
            file_content = temp
        with open("/var/www/html/admin_rancid/temporales/hosts_test", "w+") as fl:
            fl.seek(0)
            fl.write(file_content)
            fl.truncate()
        output = subprocess.Popen("sudo -u root /var/www/html/admin_rancid/replace_hosts.sh", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
        self.dspl.append_content('test','pre', str(output.stdout.read()))
        output = subprocess.Popen("sudo -u rancid /var/www/html/admin_rancid/add_key.sh " + new_device['hostname'] + "," + new_device['ip'], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
        self.dspl.append_content('test','pre', str(output.stdout.read()))


    def edit_racid_conf(self, new_device):
        output = subprocess.Popen(
             "sudo -u rancid /var/www/html/admin_rancid/add_customer.sh " + \
                 new_device['cliente'].replace(" ","_"),
             shell=True,
             stdin=subprocess.PIPE,
             stdout=subprocess.PIPE,
             stderr=subprocess.STDOUT,
             close_fds=True
             )
        self.dspl.append_content('test','pre', str(output.stdout.read()))

    def edit_routerdb(self, new_device):
        output = subprocess.Popen(
            "sudo -u rancid /var/www/html/admin_rancid/add_devicetodb.sh " + \
                new_device['hostname'] + " " + \
                (
                    'porqueria' if new_device['marca']=="CISCO-SGXXX" else \
                    # 'fortigate' if new_device['dispositivo'] == 'firewall' else \
                     new_device['marca'].lower()
                ) + " " + \
                new_device['cliente'].replace(" ","_"),
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            close_fds=True
            )
        self.dspl.append_content('test','pre', str(output.stdout.read()))

    def first_bk(self, new_device):
        output = subprocess.Popen("sudo -u rancid /var/www/html/admin_rancid/first_bk.sh " + " ".join([new_device['hostname'],new_device['cliente'],new_device['ip'],new_device['marca'],os.environ.get("REMOTE_USER","NO_USER")] ) , shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
        self.dspl.append_content('test','pre', str(output.stdout.read()))

    def insert_db(self, new_device):
        register = {}
        engine = create_engine(f"mysql+mysqldb://{db_user}:{db_pass}@{db_host}/{db_name}")
        query = """INSERT INTO csctoolmaster.rancid__cpe__legacy(customer, country, city, branch, cid, id_sccd, cid_rel, network, ip, device, vendor, customer_summary, other_id, hostname, user, date)
                VALUES(:customer, :country, :city, :branch, :cid, :id_sccd,:cid_rel, :network, :ip, :device, :vendor, :customer_summary, :other_id, :hostname, :user, :date)"""

        register['customer'] = new_device['cliente']
        register['country'] = new_device['pais']
        register['city'] = new_device['ciudad']
        register['branch'] = new_device['sede']
        register['cid'] = new_device['id']
        register['id_sccd'] = new_device['id_sccd']
        register['cid_rel'] = new_device['id_rel']
        if 'red' not in new_device:
            new_device['red'] = ""
        register['network'] = new_device['red']
        register['ip'] = new_device['ip']
        register['device'] = new_device['dispositivo']
        register['vendor'] = new_device['marca']
        register['customer_summary'] = new_device['maximo']
        register['other_id'] = new_device['funcion']
        register['hostname'] = new_device['hostname']
        register['user'] = os.environ.get("REMOTE_USER","NO_USER").lower()
        register['date'] = datetime.datetime.now()

        with engine.connect() as con:
            statement = text(query)
            result = con.execute(statement, **register)
            legacy_id = result.lastrowid
            time.sleep(3)

            if new_device.get('ip_2'):
                try:
                    upd = con.execute(text("UPDATE net_inventory__devices SET ip_2 = :ip2 WHERE rancid_id = :rid"), {'ip2': new_device['ip_2'], 'rid': legacy_id})
                    with open(LOG_PATH,'a') as f:
                        f.write("UPDATE rows=%s for rid=%s ip_2=%s\n" % (upd.rowcount, legacy_id, new_device['ip_2']))
                except Exception as e:
                    with open('/tmp/ip2_debug.log','a') as f:
                        f.write("ERROR updating ip_2: %s\n" % str(e))

            rel_cid = new_device.get('relation_cid')
            typ_rel = new_device.get('relation_type')
            if rel_cid and typ_rel:
                new_type = 'WORKING' if typ_rel == 'PROTECTION' else 'PROTECTION'
                row = con.execute(text("SELECT rancid_id FROM net_inventory__devices WHERE cid_mgt = :cid"),{'cid': rel_cid}).fetchone()
                if row:
                    related_rid = row[0]
                    con.execute(text("UPDATE net_inventory__devices SET relation = :related, type = :newt WHERE rancid_id = :rid"),{'related': related_rid, 'newt': new_type, 'rid': legacy_id})
                    con.execute(text("UPDATE net_inventory__devices SET relation = :rid, type = :typ WHERE rancid_id = :relrid"),{'rid': legacy_id, 'typ': typ_rel, 'relrid': related_rid})

        if register['vendor'] == 'ruckus-sz':
            ip = register['ip']
            name = register['id_sccd']
            customer = '_'.join([register['customer'], register['country'], register['city'], register['branch'], register['cid']])

            query_insert = """INSERT INTO aplications.ruckus_controllers (`type`, url, `user`, password, name, customer) VALUES (:tipo, :url, :user, :password, :name, :customer)"""

            register = {
                'tipo' : 'smartzone',
                'url' : f"https://{ip}:{ruckus_register_port}",
                'user' : ruckus_register_user,
                'password' : ruckus_register_pass,
                'name' : name,
                'customer' : customer
            }

            applications_db = create_engine(f"mysql+mysqldb://{applications_user}:{applications_pass}@{applications_host}/{applications_name}")

            with applications_db.connect() as con:
                statement = text(query_insert)

                con.execute(statement, **register)

            ####################################################################################################
            # INSERT INTO TM RUCKUS MONITOR ####################################################################
            ####################################################################################################
            query_insert = """INSERT INTO net_monitoring_ruckusapi__controllers(type,url,user,password,cid,customer,location,updated_at,created_at) values (:tipo,:url,:user,:password,:cid,:customer,:location, UTC_TIMESTAMP(),UTC_TIMESTAMP()) """
            register = {
                'tipo' : 'smartzone',
                'url' : f"https://{ip}:{ruckus_register_port}",
                'user' : ruckus_register_user,
                'password' : ruckus_register_pass,
                'cid' : register['cid'],
                'customer' : register['customer'],
                'location' : '_'.join([register['country'], register['city'], register['branch']])
            }

            
            applications_db = create_engine(f"mysql+mysqldb://{ruckus_user}:{ruckus_pass}@{db_host}/{db_name}")

            with applications_db.connect() as con:
                statement = text(query_insert)

                con.execute(statement, **register)

    def return_form(self, insert_to, form):
        self.dspl.insert_content(insert_to,'nota','h1',"Ingreso Nuevo Equipo")
        self.dspl.insert_content(insert_to,'nota','h4',"<b>Nota:</b> No hacer uso de caracteres especiales")
        self.dspl.insert_content(insert_to,'hidden','hidden', [], {'name' : 'step', 'value':2})
        #if form['dispositivo'] == 'firewall':
        #    self.new_firewall(insert_to, form['dispositivo'], form)
        #else:
        #    self.new_informacion_sede_cliente(insert_to, form)
        #    self.new_informacion_servicio(insert_to, form['dispositivo'], form)
        #    self.new_informacion_equipo(insert_to, form['dispositivo'], form)
        self.new_informacion_sede_cliente(insert_to, form)
        self.new_informacion_servicio(insert_to, form['dispositivo'], form)
        self.new_informacion_equipo(insert_to, form['dispositivo'], form)
        self.dspl.insert_content(insert_to,'br','newline')
        # self.dspl.insert_content(insert_to,'submit','submit',"VALIDAR E INGRESAR")
        # self.dspl.insert_content(insert_to,'submit','submit',"PROBAR HOSTNAME")
        self.dspl.insert_content(insert_to,'hidden','hidden-id', [], {'name' : 'submit_value', 'value':'', 'id' : 'tosubmit'})
        self.dspl.insert_content(insert_to,'button','button-onclick', "VALIDAR E INGRESAR", {'onclick':'this.disabled=true;document.getElementById(\'tosubmit\').value=\'VALIDAR E INGRESAR\';document.getElementById(\'f_ingreso\').submit()'})
        self.dspl.insert_content(insert_to,'button','button-onclick', "PROBAR HOSTNAME", {'onclick':'this.disabled=true;document.getElementById(\'tosubmit\').value=\'PROBAR HOSTNAME\';document.getElementById(\'f_ingreso\').submit()'})


    def formulario(self, insert_to, form):
        if form['step'] == "1":
            form2 = None
        else:
            form2 = form
        self.dspl.insert_content(insert_to,'nota','h1',"Ingreso Nuevo Equipo")
        self.dspl.insert_content(insert_to,'nota','h4',"<b>Nota:</b> No hacer uso de caracteres especiales")
        self.dspl.insert_content(insert_to,'hidden','hidden', [], {'name' : 'step', 'value':2})
        #if form['dispositivo'] == 'firewall':
        #    self.new_firewall(insert_to, form['dispositivo'], form2)
        #else:
        #    self.new_informacion_sede_cliente(insert_to, form2)
        #    self.new_informacion_servicio(insert_to, form['dispositivo'], form2)
        #    self.new_informacion_equipo(insert_to, form['dispositivo'], form2)
        self.new_informacion_sede_cliente(insert_to, form2)
        self.new_informacion_servicio(insert_to, form['dispositivo'], form2)
        self.new_informacion_equipo(insert_to, form['dispositivo'], form2)
        self.dspl.insert_content(insert_to,'br','newline')
        # self.dspl.insert_content(insert_to,'submit','submit',"VALIDAR E INGRESAR")
        # self.dspl.insert_content(insert_to,'submit','submit',"PROBAR HOSTNAME")
        self.dspl.insert_content(insert_to,'hidden','hidden-id', [], {'name' : 'submit_value', 'value':'', 'id' : 'tosubmit'})
        self.dspl.insert_content(insert_to,'button','button-onclick', "VALIDAR E INGRESAR", {'onclick':'this.disabled=true;document.getElementById(\'tosubmit\').value=\'VALIDAR E INGRESAR\';document.getElementById(\'f_ingreso\').submit()'})
        self.dspl.insert_content(insert_to,'button','button-onclick', "PROBAR HOSTNAME", {'onclick':'this.disabled=true;document.getElementById(\'tosubmit\').value=\'PROBAR HOSTNAME\';document.getElementById(\'f_ingreso\').submit()'})


    def ingreso_informacion(self, form = None):
        if form == None:
            self.dspl.append_content('form','form',[],{'action' : '/admin_rancid/rancid/ingreso'})
            self.dspl.insert_content('form','hidden','hidden', [], {'name' : 'dispositivo', 'value':'router'})
            self.dspl.insert_content('form','hidden','hidden', [], {'name' : 'step', 'value':1})
            self.dspl.insert_content('form','submit','submit','ROUTER')

            self.dspl.append_content('br','newline')

            self.dspl.append_content('form','form',[],{'action' : '/admin_rancid/rancid/ingreso'})
            self.dspl.insert_content('form','hidden','hidden', [], {'name' : 'dispositivo', 'value':'switch'})
            self.dspl.insert_content('form','hidden','hidden', [], {'name' : 'step', 'value':1})
            self.dspl.insert_content('form','submit','submit','SWITCH')

            self.dspl.append_content('br','newline')

            self.dspl.append_content('form','form',[],{'action' : '/admin_rancid/rancid/ingreso'})
            self.dspl.insert_content('form','hidden','hidden', [], {'name' : 'dispositivo', 'value':'stack'})
            self.dspl.insert_content('form','hidden','hidden', [], {'name' : 'step', 'value':1})
            self.dspl.insert_content('form','submit','submit','STACK')

            self.dspl.append_content('br','newline')

            self.dspl.append_content('form','form',[],{'action' : '/admin_rancid/rancid/ingreso'})
            self.dspl.insert_content('form','hidden','hidden', [], {'name' : 'dispositivo', 'value':'firewall'})
            self.dspl.insert_content('form','hidden','hidden', [], {'name' : 'step', 'value':1})
            self.dspl.insert_content('form','submit','submit','FIREWALL')

            self.dspl.append_content('br','newline')

            self.dspl.append_content('form','form',[],{'action' : '/admin_rancid/rancid/ingreso'})
            self.dspl.insert_content('form','hidden','hidden', [], {'name' : 'dispositivo', 'value':'traficmanager'})
            self.dspl.insert_content('form','hidden','hidden', [], {'name' : 'step', 'value':1})
            self.dspl.insert_content('form','submit','submit','TRAFFIC MANAGER')

            self.dspl.append_content('br','newline')

            self.dspl.append_content('form','form',[],{'action' : '/admin_rancid/rancid/ingreso'})
            self.dspl.insert_content('form','hidden','hidden', [], {'name' : 'dispositivo', 'value':'wifi'})
            self.dspl.insert_content('form','hidden','hidden', [], {'name' : 'step', 'value':1})
            self.dspl.insert_content('form','submit','submit','WIFI')

            self.dspl.append_content('br','newline')

            self.dspl.append_content('form','form',[],{'action' : '/admin_rancid/rancid/ingreso'})
            self.dspl.insert_content('form','hidden','hidden', [], {'name' : 'dispositivo', 'value':'audiocodes'})
            self.dspl.insert_content('form','hidden','hidden', [], {'name' : 'step', 'value':1})
            self.dspl.insert_content('form','submit','submit','AUDIOCODES')
        else:
            self.dspl.append_content('form','form-id',[],{'action' : '/admin_rancid/rancid/ingreso', 'id' : 'f_ingreso'})
            self.dspl.insert_content('form','hidden','hidden', [], {'name' : 'dispositivo', 'value':form['dispositivo']})
            if form['step'] == '1':
                self.formulario('form',form)
            elif form['step'] == '2':
                # validar retornar con texto, y si falla alguno retornar con valores
                #  Modificacion 2021_06_04 validacion longitud del hostname
                val_result = self.form_validate(form)
                if val_result is False:
                    new_device = self.preproces(form)
                    if len(new_device['hostname']) > 145:
                        val_result = True
                        self.dspl.append_content('pre','p',"<br/>Hostname muy largo!!<br/><br/>" + new_device["hostname"] )
                # Fin modificacio 2021_06_04
                if val_result is False :
                    new_device = self.preproces(form)
                    if form['submit_value'] == "PROBAR HOSTNAME":
                        self.dspl.insert_content('main','text','text', new_device['hostname'])
                        self.return_form('form',form)
                    else:
                        temp111= ""
                        for n in form:
                            temp111 += n + " : " + str(form[n]) + "<br>"
                        self.dspl.append_content('algo','div',temp111)

                        wait_error_counter = 60
                        while os.path.isfile("running_files/editing_hosts") :
                            time.sleep(1)
                            wait_error_counter -= 1
                            if wait_error_counter <= 0:
                                raise Exception('Limite tiempo de espera editing_host')
                        os.system("touch running_files/editing_hosts")
                        self.edit_hosts(new_device)
                        if new_device['isnew']:
                            self.edit_racid_conf(new_device)
                        self.edit_routerdb(new_device)
                        os.system("rm running_files/editing_hosts")
                        os.system("echo " + str(new_device) + "> running_files/new_device")
                        self.insert_db(new_device)
                        self.first_bk(new_device)
            else:
                self.formulario('form',form)


    def get(self):
        if self.curr_script == 'ips':
            self.dspl.set_content('<h2>IPS</h2><iframe src="/ips" width=1200 height=500></iframe>')
        elif self.curr_script == 'resumen':
            self.dspl.set_content('<h2>RESUMEN</h2><iframe src="/resumen" width=1200 height=500></iframe>')
        elif self.curr_script == 'respaldos':
            self.dspl.set_content('<h2>RESPALDOS</h2><iframe src="/viewvc" width=1200 height=500></iframe>')
        elif self.curr_script == 'ingreso':
            self.ingreso_informacion()
        else:
            print(f"Location: {self.ctr_data['root_html']}{"/".join(['rancid','ips'])}")

    def post(self,form):
        if self.curr_script == 'ingreso':
            self.ingreso_informacion(form)