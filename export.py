#!/usr/bin/env python
import sqlite3
import yaml
from models import *

con = sqlite3.connect('cv.db')
con.row_factory = sqlite3.Row
cur = con.cursor()

res = cur.execute("""
                  select title, employer, location, strftime('%Y-%m', start) as start_date,
                  strftime('%Y-%m', end) as end_date from roles order by start desc
                  """).fetchall()

roles = [Role(**r) for r in res]

res = cur.execute("""
                  select categories.category, skills.skill from categories 
                  join skill_categories on categories.rowid = skill_categories.category
                  join skills on skill_categories.skill = skills.rowid
                  order by categories.category asc, skills.skill asc
                  """).fetchall()

categories = {r: Category(r) for r in sorted(set([row["category"] for row in res]))}
skills = {r: Skill(r, 'Good') for r in sorted(set([row["skill"] for row in res]))}

for row in res:
    categories[row["category"]].skills.append(skills[row["skill"]])


res = cur.execute("""
                  select a.rowid as a_id, a.detail, skills.skill as s, roles.rowid as role_id, 
                  roles.employer, roles.title, roles.location,
                  strftime('%Y-%m', roles.start) as start_date, strftime('%Y-%m', roles.end) as end_date
                  from achievements as a
                  join achievement_skills on a_id = achievement_skills.achievement
                  join skills on achievement_skills.skill = skills.rowid
                  left outer join achievement_roles on a_id = achievement_roles.achievement
                  left outer join roles on achievement_roles.`role` = role_id
                  order by roles.start desc, a_id asc
                  """).fetchall()
doc["history"] = [a | {
    "achievements": list(a["achievements"].values()),
} for a in reduce(munge_history, res, {}).values()]

doc = {
    "competencies": [Competency(c) for c in Competency],
    "skills": list(skills.values()),
    "categories": list(categories.values()),
    "roles": roles,
}

stream = open('cv.yaml', 'w')
yaml.dump(doc, stream, indent=2, width=500, sort_keys=False)

# stream = open('cv.yaml', 'r')
# print(yaml.load(stream, Loader=yaml.Loader))

con.close()