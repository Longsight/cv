#!/usr/bin/env python
import sqlite3
import yaml
from functools import reduce
from enum import auto, StrEnum

con = sqlite3.connect('cv.db')
con.row_factory = sqlite3.Row
cur = con.cursor()

categories = {}
skills = {}

class SkillLevel(StrEnum):
    POOR = auto()
    RUSTY = auto()
    GOOD = auto()
    EXCELLENT = auto()
    def __str__(self):
        return f'{self.name}'.title()
    @classmethod
    def _missing_(cls, value):
        if value is None:
            return SkillLevel.POOR
        value = value.lower()
        for member in cls:
            if member.value == value:
                return member
        return SkillLevel.POOR

class Skill(yaml.YAMLObject):
    yaml_tag = u'!Skill'
    def __init__(self, name, level):
        self.name = name
        self.level = SkillLevel(level)
    def __repr__(self):
        return "%s(name=%r, level=%r)" % (
            self.__class__.__name__, self.name, self.level)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_scalar(u'!Skill', data.level)

    @classmethod
    def from_yaml(cls, loader, node):
        data = {
            "name": node,
            "level": SkillLevel(loader.construct_scalar(node))
        }
        return data

class Category(yaml.YAMLObject):
    yaml_tag = u'!Category'
    def __init__(self, name):
        self.name = name
        self.skills = []
    def add_skill(self, skill):
        if skill in skills:
            self.skills.append(skills[skill])
    def __repr__(self):
        return "%s(name=%r, skills=%r)" % (
            self.__class__.__name__, self.name, self.skills)
    
class Role(yaml.YAMLObject):
    yaml_tag = u'!Role'
    def __init__(self, employer, title, location, start_date, end_date):
        self.employer = employer
        self.title = title
        self.location = location
        self.start_date = start_date
        self.end_date = end_date
    def __repr__(self):
        return "%s(employer=%r, title=%r, location=%r, start_date=%r, end_date=%r)" % (
            self.__class__.__name__, self.employer, self.title, self.location, self.start_date, self.end_date)
    
# def munge_skills(memo, row):
#     try:
#         skill = memo[row["category"]]
#     except KeyError:
#         memo[row["category"]] = []

#     memo[row["category"]].append(row["skill"])

#     return memo

# def munge_history(memo, row):
#     role = row["role_id"]
#     try:
#         role = memo[row["role_id"]]
#     except KeyError:
#         memo[row["role_id"]] = {
#             "employer": row["employer"],
#             "title": row["title"],
#             "location": row["location"],
#             "start_date": row["start_date"],
#             "end_date": row["end_date"],
#             "achievements": {}
#         }

#     try:
#         achievements = memo[row["role_id"]]["achievements"][row["a_id"]]
#     except KeyError:
#         memo[row["role_id"]]["achievements"][row["a_id"]] = { "details": row[1], "skills": [] }

#     memo[row["role_id"]]["achievements"][row["a_id"]]["skills"].append(row[2])

#     return memo

doc = {}

res = cur.execute("""
                  select title, employer, location, strftime('%Y-%m', start) as start_date,
                  strftime('%Y-%m', end) as end_date from roles order by start desc
                  """).fetchall()
doc["roles"] = [dict(r) for r in res]

res = cur.execute("""
                  select categories.category, skills.skill from categories 
                  join skill_categories on categories.rowid = skill_categories.category
                  join skills on skill_categories.skill = skills.rowid
                  order by categories.category asc, skills.skill asc
                  """).fetchall()
categories = {r: Category(r) for r in sorted(set([row["category"] for row in res]))}
skills = {r: Skill(r, None) for r in sorted(set([row["skill"] for row in res]))}

doc["categories"] = categories
doc["skills"] = skills


# res = cur.execute("""
#                   select a.rowid as a_id, a.detail, skills.skill as s, roles.rowid as role_id, 
#                   roles.employer, roles.title, roles.location,
#                   strftime('%Y-%m', roles.start) as start_date, strftime('%Y-%m', roles.end) as end_date
#                   from achievements as a
#                   join achievement_skills on a_id = achievement_skills.achievement
#                   join skills on achievement_skills.skill = skills.rowid
#                   left outer join achievement_roles on a_id = achievement_roles.achievement
#                   left outer join roles on achievement_roles.`role` = role_id
#                   order by roles.start desc, a_id asc
#                   """).fetchall()
# doc["history"] = [a | {
#     "achievements": list(a["achievements"].values()),
# } for a in reduce(munge_history, res, {}).values()]

stream = open('cv.yaml', 'r')
# yaml.dump(doc, stream, indent=2, width=500, sort_keys=False)
print(yaml.load(stream, Loader=yaml.Loader))

con.close()