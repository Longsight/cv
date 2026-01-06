#!/usr/bin/env python
import sqlite3
import yaml
from models import *

con = sqlite3.connect('cv.db')
con.row_factory = sqlite3.Row
cur = con.cursor()

res = cur.execute("""
                  select skills.name, skills.competency from skills
                  order by skills.name asc
                  """).fetchall()

skills = {r["name"]: Skill(**r) for r in res}

res = cur.execute("""
                  select categories.name, skills.name as skill from categories 
                  join skill_categories on categories.category_id = skill_categories.category_id
                  join skills on skill_categories.skill_id = skills.skill_id
                  order by categories.name asc, skill asc
                  """).fetchall()

categories = {r["name"]: Category(**r) for r in res}

for row in res:
    categories[row["name"]].skills.append(skills[row["skill"]])

res = cur.execute("""
                  select achievements.achievement_id, achievements.detail, skills.name as skill, roles.role_id, 
                  roles.employer, roles.title, roles.location,
                  strftime('%Y-%m-%d', roles.start_date) as start_date, strftime('%Y-%m-%d', roles.end_date) as end_date
                  from achievements
                  join skill_achievements on achievements.achievement_id = skill_achievements.achievement_id
                  join skills on skill_achievements.skill_id = skills.skill_id
                  left outer join roles on achievements.role_id = roles.role_id
                  order by roles.start_date desc, achievements.achievement_id asc
                  """).fetchall()

roles = {r.employer: r for r in sorted(set([Role(**row) for row in res]))}
achievements = {r.detail: r for r in set([Achievement(roles[row['employer']], **row) for row in res])}

for row in res:
    achievements[row['detail']].skills.append(skills[row["s"]])

doc = {
    "competencies": [Competency(c) for c in Competency],
    "skills": list(skills.values()),
    "categories": list(categories.values()),
    "roles": list(roles.values()),
    "achievements": list(achievements.values()),
}

print(yaml.dump(doc, indent=2, width=500, sort_keys=False))

con.close()