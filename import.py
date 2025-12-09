#!/usr/bin/env python
import sqlite3
import re
from xml.etree import ElementTree

tree = ElementTree.parse('index.html')

con = sqlite3.connect('cv.db')
cur = con.cursor()

for group in tree.findall('.//div/ul/li'):
    try:
        employers = group.attrib['employer'].split(',')
    except:
        employers = []

    for achievement in group.findall('./ul/li'):
        detail = achievement.text
        try:
            skills = achievement.attrib['skills'].split(',')
        except:
            skills = []

        try:
            achievement_employers = achievement.attrib['employer'].split(',')
        except:
            achievement_employers = employers

        if detail:
            res = cur.execute('select rowid from achievements where detail = ?', (detail, )).fetchone()
            if res is None:
                cur.execute('insert into achievements (detail) values (?)', (detail, ))
                con.commit()
                print('Inserted achievement "%s"' % (detail, ))
                achievement_id = cur.lastrowid
            else:
                achievement_id = res[0]

            for skill in skills + re.split(r'[.,]* ', detail):
                res = cur.execute('select rowid from skills where skill = ? collate nocase', (skill, )).fetchone()
                if not res is None:
                    skill_id = res[0]
                    res = cur.execute('select rowid from achievement_skills where achievement = ? and skill = ?', (achievement_id, skill_id, )).fetchone()
                    if res is None:
                        cur.execute('insert into achievement_skills (achievement, skill) values (?, ?)', (achievement_id, skill_id, ))
                        print('Inserted link between achievement %d and skill "%s"' % (achievement_id, skill))

            for employer in [emp for emp in achievement_employers if emp]:
                res = cur.execute('select rowid from roles where employer = ? collate nocase', (employer, )).fetchone()
                if not res is None:
                    role_id = res[0]
                    res = cur.execute('select rowid from achievement_roles where achievement = ? and `role` = ?', (achievement_id, role_id, )).fetchone()
                    if res is None:
                        cur.execute('insert into achievement_roles (achievement, `role`) values (?, ?)', (achievement_id, role_id, ))
                        print('Inserted link between achievement %d and employer "%s"' % (achievement_id, employer))

            con.commit()
con.close()