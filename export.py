#!/usr/bin/env python
import sys
import sqlite3
import yaml
from itertools import groupby
from jinja2 import Environment, PackageLoader, select_autoescape

from models import *

con = sqlite3.connect('cv.db')
con.row_factory = sqlite3.Row
cur = con.cursor()

try:
    version = sys.argv[1]
    all = 0
    res = cur.execute("select slug from versions where name = ?", (version, )).fetchone()
except IndexError:
    version = ""
    all = 1
    count = 500
    res = cur.execute("select slug from versions where name = 'platform-engineer'").fetchone()

if all == 0:
    try:
        count = sys.argv[2]
    except IndexError:
        count = 40

try:
    slug = res['slug']
except TypeError:
    print("version %s not found" % version)
    sys.exit(1)

res = cur.execute("""
                  select skills.name, skills.competency from skills
                  join skill_categories on skill_categories.skill_id = skills.skill_id
                  join version_categories on version_categories.category_id = skill_categories.category_id
                  join versions on version_categories.version_id = versions.version_id
                  where versions.name = ? or 1 = ?
                  group by skills.name
                  order by lower(skills.name) asc
                  """, (version, all, )).fetchall()

skills = [Skill(**row) for row in res]

res = cur.execute("""
                  select roles.role_id, roles.employer, roles.title, roles.location,
                  strftime('%Y-%m-%d', roles.start_date) as start_date, 
                  strftime('%Y-%m-%d', roles.end_date) as end_date
                  from roles order by roles.start_date desc
                  """).fetchall()

roles = [Role(**row) for row in res]

res = cur.execute("""
                  select education.*
                  from education order by education.start_date desc
                  """).fetchall()

education = [Education(**row) for row in res]

res = cur.execute("""
                  select achievements.achievement_id, achievements.detail, 
                  group_concat(
                    distinct concat(skills.name, ':', skills.competency) order by lower(skills.name) asc
                  ) as skills,
                  roles.employer as employer, roles.title as role, roles.location,
                  strftime('%Y-%m-%d', roles.start_date) as start_date,
                  strftime('%Y-%m-%d', roles.end_date) as end_date
                  from achievements join skill_achievements
                  on achievements.achievement_id = skill_achievements.achievement_id
                  join skills on skill_achievements.skill_id = skills.skill_id
                  join skill_categories on skill_categories.skill_id = skills.skill_id
                  join version_categories on version_categories.category_id = skill_categories.category_id
                  join versions on version_categories.version_id = versions.version_id
                  left outer join roles on achievements.role_id = roles.role_id
                  where versions.name = ? or 1 = ?
                  group by achievements.detail
                  order by roles.start_date desc, achievements.achievement_id asc
                  limit ?
                  """, (version, all, count, )).fetchall()

achievements = [Achievement(**row) for row in res]

con.close()

doc = {
    "version": version,
    "slug": slug,
    "education": education,
    "skills": skills,
    "roles": roles,
    "achievements": achievements,
}

env = Environment(
    loader=PackageLoader("export"),
    autoescape=select_autoescape()
)
template = env.get_template("index.html")
with open("versions/%s.html" % (version if version != "" else "all"), "w") as file:
    file.write(template.render(doc))

