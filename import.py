#!/usr/bin/env python
import sqlite3
import yaml
from models import *

con = sqlite3.connect('cv.db')
con.row_factory = sqlite3.Row
cur = con.cursor()

stream = open('cv.yaml', 'r')
tree = yaml.load(stream, Loader=yaml.Loader)



con.close()