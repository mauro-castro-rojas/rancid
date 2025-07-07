#!/usr/bin/python
import cgi
import cgitb
import os
from modctrl import *

cgitb.enable()

web = Modctrl()
web.run()