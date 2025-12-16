#!/usr/bin/env python
import sqlite3
import yaml
from models import *

con = sqlite3.connect('cv.db')
con.row_factory = sqlite3.Row
con.execute('pragma foreign_keys = ON')

stream = open('cv.yaml', 'r')
tree = yaml.load(stream, Loader=yaml.Loader)

with con:
    try:
        con.executescript('''
            PRAGMA FOREIGN_KEYS = ON;
            BEGIN;
            CREATE TABLE skills (name text primary key, competency text);
            CREATE TABLE roles (employer text primary key, title text, location text, start_date text, end_date text);
            CREATE TABLE categories (name text primary key);
            CREATE TABLE achievements(detail text primary key, role_id text,
                                   foreign key(role_id)references roles(employer));
            CREATE TABLE skill_categories(skill_id text, category_id text,
                                   foreign key(skill_id) references skills(name) on update cascade on delete cascade,
                                   foreign key(category_id) references categories(name) on update cascade on delete cascade);
            CREATE TABLE skill_achievements(skill_id text, achievement_id text,
                                   foreign key(skill_id) references skills(name) on update cascade on delete cascade,
                                   foreign key(achievement_id) references achievements(detail) on update cascade on delete cascade);
            CREATE TABLE versions (name text primary key);
            CREATE TABLE version_categories (version_id text, category_id text,
                                   foreign key(version_id) references versions(name) on update cascade on delete cascade,
                                   foreign key(category_id) references categories(name) on update cascade on delete cascade);
            COMMIT;
        ''')
    except sqlite3.OperationalError:
        pass

    for s in tree['skills']:
        try:
            con.execute('insert into skills values (?, ?)', (s.name, s.competency, ))
        except sqlite3.IntegrityError:
            pass

    for c in tree['categories']:
        try:
            con.execute('insert into categories values (?)', (c.name, ))
            con.executemany(
                'insert into skill_categories (skill_id, category_id) values (?, ?)',
                [(s.name, c.name,) for s in c.skills])
        except sqlite3.IntegrityError:
            pass

    for r in tree['roles']:
        try:
            con.execute('insert into roles values (?, ?, ?, ?, ?)',
                        (r.employer, r.title, r.location,
                         r.start_date.strftime('%Y-%m-%d') if r.start_date else None,
                         r.end_date.strftime('%Y-%m-%d') if r.end_date else None, ))
        except sqlite3.IntegrityError:
            pass

    for a in tree['achievements']:
        try:
            con.execute('insert into achievements values (?, ?)', (a.detail, a.role.employer, ))
            con.executemany(
                'insert into skill_achievements (skill_id, achievement_id) values (?, ?)',
                [(s.name, a.detail,) for s in a.skills])
        except sqlite3.IntegrityError:
            pass

con.close()