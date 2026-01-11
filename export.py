#!/usr/bin/env python
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

res = cur.execute("""
                  select skills.name, skills.competency from skills
                  order by skills.name asc
                  """).fetchall()

skills = list(set([Skill(**row) for row in res]))

# res = cur.execute("""
#                   select categories.name, skills.name as skill, skills.competency from categories 
#                   join skill_categories on categories.category_id = skill_categories.category_id
#                   join skills on skill_categories.skill_id = skills.skill_id
#                   order by categories.name asc, skill asc
#                   """).fetchall()

# categories = group_rows(Category, res, "name")

res = cur.execute("""
                  select roles.role_id, roles.employer, roles.title, roles.location,
                  strftime('%Y-%m-%d', roles.start_date) as start_date, 
                  strftime('%Y-%m-%d', roles.end_date) as end_date
                  from roles order by roles.start_date desc
                  """).fetchall()

roles = list(sorted(set([Role(**row) for row in res])))

res = cur.execute("""
                  select achievements.achievement_id, achievements.detail, skills.name as skill,
                  skills.competency, roles.employer as role from achievements join skill_achievements
                  on achievements.achievement_id = skill_achievements.achievement_id
                  join skills on skill_achievements.skill_id = skills.skill_id
                  left outer join roles on achievements.role_id = roles.role_id
                  order by roles.start_date desc, achievements.achievement_id asc
                  """).fetchall()

achievements = group_rows(Achievement, res, "detail", sort=True)

doc = {
    "skills": skills,
    "roles": roles,
    "achievements": achievements,
}

print(yaml.dump(doc, indent=2, width=500, sort_keys=False))

con.close()