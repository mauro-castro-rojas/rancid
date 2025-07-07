import pexpect, cgi,json, os, time, shlex
from datetime import datetime

class LogtoVar(object):
    def __init__(self):
        self.file = ""

    def write(self, data):
        self.file += str(data)
        return 0

    def read(self):
        return self.file

    def flush(self):
        pass

class Cisco:
    base_prompt = "#$"
    conf_prompt = "#$"
    no_more = "terminal length 0"
    prompt_options = ["#$", "\?$","confirm"]

    @staticmethod
    def salir(child):
        child.sendline('exit')

    @staticmethod
    def guardar_salir(child):
        child.child.sendline("copy running-config startup-config")
        child.expect("?$")
        child.send("\n")
        i = child.expect( ["confirm", "#$"])
        if i == 0:
            child.send("\n")
            child.expect("#$")
        elif i==1:
            pass
        child.sendline("exit")

    @staticmethod
    def ssh(child):
        child.sendline("configure terminal")
        child.expect("#$")
        child.sendline("ip domain-name columbus.co")
        child.expect("#$")
        child.sendline("crypto key generate rsa modulus 1024")
        child.expect("#$")
        child.sendline("ip ssh version 2")
        child.expect("#$")
        child.sendline("end\n")

    @staticmethod
    def usuario(child):
        child.sendline("configure terminal")
        child.expect("#$")
        child.sendline("username admin privi 15 secr 0 c0Lumbu$")
        child.expect("#$")
        child.sendline("end")

class Juniper:
    base_prompt = "> $"
    conf_prompt = "# $"
    no_more = "set cli screen-length 0"
    prompt_options = ["> $", "# $", "[Pp]assword:"]

    @staticmethod
    def salir(child):
        child.sendline("exit")

    @staticmethod
    def usuario(child):
        child.sendline("configure")
        child.expect("# $")
        child.sendline("set system login user admin authentication plain-text-password")
        child.expect("[Pp]assword:")
        child.sendline("c0Lumbu$")
        child.expect("[Pp]assword:")
        child.sendline("c0Lumbu$")
        child.expect("# $")
        child.sendline("set system root-authentication plain-text-password")
        child.expect("[Pp]assword:")
        child.sendline("c0Lumbu$")
        child.expect("[Pp]assword:")
        child.sendline("c0Lumbu$")
        child.expect("# $")
        child.sendline("set system login retry-options tries-before-disconnect 4")
        child.expect("# $")
        child.sendline("set system login retry-options lockout-period 2")
        child.expect("# $")
        child.sendline("set system login class super-user-local idle-timeout 5")
        child.expect("# $")
        child.sendline("set system login class super-user-local permissions all")
        child.expect("# $")
        child.sendline("set system login user admin class super-user-local")
        child.expect("# $")
        child.sendline("commit")
        child.expect("# $")
        child.sendline("exit")

class SmallBusiness:
    base_prompt = "#$"
    conf_prompt = "#$"
    no_more = "terminal datadump"
    prompt_options = [ "#$", "\?$"]

    @staticmethod
    def guardar_salir(child):
        child.sendline("copy running-config startup-config")
        child.expect("?")
        child.sendline("Y")
        child.expect("#$")
        child.sendline("exit")

    @staticmethod
    def salir(child):
        child.sendline("exit")

    @staticmethod
    def usuario(child):
        child.sendline("configure terminal")
        child.expect("#$")
        child.sendline("username admin password c0Lumbu$ privilege 15")
        child.expect("#$")
        child.sendline("end")

    @staticmethod
    def ssh(child):
        child.sendline("configure terminal")
        child.expect("#$")
        child.sendline("ip ssh server")
        child.expect("#$")
        child.sendline("end")

class BaseExpect:
    admin_Username="admin"
    admin_Password="c0Lumbu$"
    admin_Password2="Columbus!"
    csc_Username="csc"
    csc_Password="csc-cwc-2016"
    temporal_Username="temporal"
    temporal_Password="temporal"
    temporal_Password2="Temporal1!"
    sid_Username="sid-ip"
    sid_Password="sid-cw-bus1n3ss"
    intentos_login=0
    dev_login=0
    CiscoDev1=1
    CiscoDev2=2
    JuniperDev1=3
    JuniperDev2=4
    SBDev1=5
    SBDev2=6

    @staticmethod
    def login_telnet(child,usr,passwd):
        child.sendline(usr)
        child.expect("assword:")
        child.sendline(passwd)

    @staticmethod
    def login(child,usr,passwd):
        child.sendline(passwd)

    @staticmethod
    def login_sb(child,usr,passwd):
        BaseExpect.login_telnet(child, usr, passwd)

    @staticmethod
    def sin_credenciales(child):
        BaseExpect.send_log(child,"\r\n\r\n\r\nsin credenciales para admin\r\n")
        BaseExpect.send_log(child,"\n### /END-SSH-SESSION/ IP: $IPaddress @ " + datetime.utcnow().isoformat() + " ###\r\n")
        child.close(force=True)

    @staticmethod
    def send_log(child, log):
        child.logfile.write(log)
        child.logfile_read.write(log)

    @staticmethod
    def start_ssh(user,ip,port=22):
        child =  pexpect.spawn(" ".join(['ssh','-o','"StrictHostKeyChecking no"','-p',str(port),user + '@' + ip]))
        child.logfile=LogtoVar()
        child.logfile_read=LogtoVar()
        return child
        #(command_output, exitstatus) = run ('ls -l /bin', withexitstatus=1)

    @staticmethod
    def start_telnet(user,ip,port=23):
        child = pexpect.spawn(" ".join(['telnet', ip, str(port)]))
        child.logfile=LogtoVar()
        child.logfile_read=LogtoVar()
        return child

    @staticmethod
    def login_1n(child,usr,passwd=[],telnet=False):
        for p in passwd:
            r = BaseExpect.login_1(child,usr,p,telnet)
            if r != 0:
                return r
        return 0

    @staticmethod
    def login_1(child,usr, passwd, telnet=False):
        if telnet:
            login_prompt = "[Uu]sername:"
            login = BaseExpect.login_telnet
        else:
            login_prompt = "[Pp]assword:"
            login = BaseExpect.login
        i = child.expect([login_prompt,"[Nn]ame:",pexpect.EOF,pexpect.TIMEOUT])
        if i == 0:
            login(child, usr, passwd)
            k = child.expect([login_prompt,"#$","> $",pexpect.EOF,pexpect.TIMEOUT])
            if k == 1:
                return BaseExpect.CiscoDev1
            elif k == 2:
                return BaseExpect.JuniperDev1
            else:
                return 0
        elif i == 1:
            BaseExpect.login_sb(child, usr, passwd)
            k = child.expect(["[Nn]ame:", "#$",pexpect.EOF, pexpect.TIMEOUT])
            if k == 1:
                return BaseExpect.SBDev1
            else:
                return 0
        else:
            return 0

    @staticmethod
    def login_n(child,IPaddress,credentials=[],telnet=False):
        if telnet:
            start_console = BaseExpect.start_telnet
        else:
            start_console = BaseExpect.start_ssh
        for login in credentials:
            child = start_console(login[0], IPaddress)
            if len(login) > 1:
                ret = BaseExpect.login_1n(child, login[0], login[1:], telnet)
            else:
                return 0
            if ret != 0:
                BaseExpect.send_log(child,"\r\n\r\n\r\n### usuario " + login[0] + " ###\r\n\r\n\r\n")
                return ret
            else:
                return 0
        BaseExpect.sin_credenciales(child)
        return 0

    @staticmethod
    def get_device(dev):
        if dev == BaseExpect.CiscoDev1 or dev == BaseExpect.CiscoDev2 :
            return Cisco
        elif dev == BaseExpect.JuniperDev1 or dev == BaseExpect.JuniperDev2 :
            return Juniper
        elif dev == BaseExpect.SBDev1 or dev == BaseExpect.SBDev2 :
            return SmallBusiness
        else:
            return None

    @staticmethod
    def send_script(child,dev,script):
        Device = BaseExpect.get_device(dev)
        if Device is None :
            #child.logfile.write("\r\n********************************\r\n No se identifica dispositivo \r\n********************************\r\n")
            BaseExpect.send_log(child,"\r\n********************************\r\n No se identifica dispositivo \r\n********************************\r\n")
            child.close()
            return 0
        else:
            BaseExpect.send_log(child,"\r\n********* SCRIPT ***************\r\n" + script + "\r\n********************************\r\n")
            prompt = Device.prompt_options
            for line in script.splitlines():
                if "#prompt" in line:
                    prompt += shlex.split(line)[1]
                elif "#conf_prompt" in line :
                    prompt += Device.conf_prompt
                elif "#base_prompt" in line :
                    prompt += Device.base_prompt
                elif "#wait" in line :
                    time.sleep(int(line.split()[1]))
                else:
                    i = child.expect( prompt + [pexpect.TIMEOUT, pexpect.EOF])
                    if i in range(len(prompt)):
                        child.sendline(line.rstrip())
                        #child.logfile.write("\r\n\r\n" + str(i) + "\r\n\r\n")
                    else:
                        child.close()
                        return 0

    @staticmethod
    def send_no_more(child,dev):
        Device = BaseExpect.get_device(dev)
        if Device is None :
            #child.logfile.write("\r\n********************************\r\n No se identifica dispositivo \r\n********************************\r\n")
            BaseExpect.send_log(child,"\r\n********************************\r\n No se identifica dispositivo \r\n********************************\r\n")
            child.close()
            return 0
        i = child.expect(Device.prompt_options + [pexpect.TIMEOUT, pexpect.EOF])
        if i in range(len(Device.prompt_options)):
            child.sendline(Device.no_more)
        else:
            child.close()

    @staticmethod
    def close_device(child, dev):
        Device = BaseExpect.get_device(dev)
        if Device is None :
            #child.logfile.write("\r\n********************************\r\n No se identifica dispositivo \r\n********************************\r\n")
            BaseExpect.send_log(child,"\r\n********************************\r\n No se identifica dispositivo \r\n********************************\r\n")
            child.close()
            return 0
        child.send("\n")
        i = child.expect([Device.base_prompt, pexpect.TIMEOUT, pexpect.EOF])
        if i == 0:
            Device.salir(child)
        else:
            child.close()

    @staticmethod
    def script(child, dev, script):
        if dev == 0:
            #child.logfile.write("\r\n********************************\r\n Sin Credenciales de Acceso \r\n********************************\r\n")
            BaseExpect.send_log(child,"\r\n********************************\r\n Sin Credenciales de Acceso \r\n********************************\r\n")
            child.close()
            return 0
        else:
            child.send("\n")
            BaseExpect.send_no_more(child,dev)
            BaseExpect.send_script(child,dev, script)
            BaseExpect.close_device(child,dev)