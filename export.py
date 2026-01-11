#!/usr/bin/env python
import sys
import sqlite3
import yaml
from itertools import groupby
from models import *

con = sqlite3.connect('cv.db')
con.row_factory = sqlite3.Row
cur = con.cursor()

def group_rows(type, rows, key_name, sort=False):
    result = []
    for key, group in groupby(rows, lambda x: x[key_name]):
        rows = list(group)
        obj = type(**rows[0])
        obj.skills = {r["skill"]: r["competency"] for r in rows}
        result.append(obj)
    if sort:
        return sorted(result)
    return result

try:
    version = sys.argv[1]
except IndexError:
    version = "dev"

res = cur.execute("select slug from versions where name = ?", (version, )).fetchone()
slug = res['slug']

res = cur.execute("""
                  select skills.name, skills.competency from skills
                  join skill_categories on skill_categories.skill_id = skills.skill_id
                  join version_categories on version_categories.category_id = skill_categories.category_id
                  join versions on version_categories.version_id = versions.version_id
                  where versions.name = ?
                  group by skills.name
                  order by lower(skills.name) asc
                  """, (version, )).fetchall()

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
                  roles.employer as employer, roles.title as role,
                  strftime('%Y-%m-%d', roles.start_date) as start_date,
                  strftime('%Y-%m-%d', roles.end_date) as end_date
                  from achievements join skill_achievements
                  on achievements.achievement_id = skill_achievements.achievement_id
                  join skills on skill_achievements.skill_id = skills.skill_id
                  join skill_categories on skill_categories.skill_id = skills.skill_id
                  join version_categories on version_categories.category_id = skill_categories.category_id
                  join versions on version_categories.version_id = versions.version_id
                  left outer join roles on achievements.role_id = roles.role_id
                  where versions.name = ?
                  group by achievements.detail
                  order by roles.start_date desc, achievements.achievement_id asc
                  """, (version, )).fetchall()

achievements = [Achievement(**row) for row in res]

doc = {
    "slug": slug,
    "education": education,
    "skills": skills,
    "roles": roles,
    "achievements": achievements,
}

print(yaml.dump(doc, indent=2, width=500, sort_keys=False))

con.close()