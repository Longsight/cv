#!/usr/bin/env python
import os
import sqlite3
import yaml
from models import *

try:
    os.remove('./cv.db')
except FileNotFoundError:
    pass

con = sqlite3.connect('./cv.db')
con.row_factory = sqlite3.Row
con.execute('pragma foreign_keys = ON')

stream = open('cv.yaml', 'r')
tree = yaml.load(stream, Loader=yaml.Loader)

with con:
    try:
        con.executescript('''
            PRAGMA FOREIGN_KEYS = ON;
            BEGIN;
            CREATE TABLE skills (skill_id integer primary key autoincrement, name text unique, competency text);
            CREATE TABLE roles (role_id integer primary key autoincrement, employer text unique, title text,
                location text, start_date text, end_date text);
            CREATE TABLE categories (category_id integer primary key autoincrement, name text unique);
            CREATE TABLE achievements(achievement_id integer primary key autoincrement, detail text unique, role_id integer,
                foreign key(role_id) references roles(role_id) on update cascade on delete set null);
            CREATE TABLE education(education_id integer primary key autoincrement, institution text unique,
                qualification text, detail text, start_date integer, end_date integer);
            CREATE TABLE skill_categories(skill_id integer, category_id integer,
                foreign key(skill_id) references skills(skill_id) on update cascade on delete cascade,
                foreign key(category_id) references categories(category_id) on update cascade on delete cascade);
            CREATE TABLE skill_achievements(skill_id integer, achievement_id integer,
                foreign key(skill_id) references skills(skill_id) on update cascade on delete cascade,
                foreign key(achievement_id) references achievements(achievement_id) on update cascade on delete cascade);
            CREATE TABLE versions (version_id integer primary key autoincrement, name text unqiue);
            CREATE TABLE version_categories (version_id integer, category_id integer,
                foreign key(version_id) references versions(version_id) on update cascade on delete cascade,
                foreign key(category_id) references categories(category_id) on update cascade on delete cascade);
            COMMIT;
        ''')
    except sqlite3.OperationalError:
        pass

    for s in tree['skills']:
        try:
            con.execute('insert into skills (name, competency) values (?, ?)', (s.name, s.competency, ))
        except sqlite3.IntegrityError:
            pass

    for c in tree['categories']:
        try:
            cur = con.execute('insert into categories (name) values (?) returning category_id', (c.name, ))
            category_id = cur.fetchone()[0]
            con.executemany(
                '''
                insert into skill_categories (skill_id, category_id) values (
                    (select skill_id from skills where name = ?), ?
                )
                ''',
                [(s.name, category_id,) for s in c.skills])
        except sqlite3.IntegrityError:
            pass

    for r in tree['roles']:
        try:
            con.execute('insert into roles (employer, title, location, start_date, end_date) values (?, ?, ?, ?, ?)',
                        (r.employer, r.title, r.location,
                         r.start_date.strftime('%Y-%m-%d') if r.start_date else None,
                         r.end_date.strftime('%Y-%m-%d') if r.end_date else None, ))
        except sqlite3.IntegrityError:
            pass

    for a in tree['achievements']:
        try:
            cur = con.execute(
                '''
                insert into achievements (detail, role_id) values (
                    ?, (select role_id from roles where employer = ?)
                ) returning achievement_id
                '''
                , (a.detail, a.role.employer, ))
            achievement_id = cur.fetchone()[0]
            con.executemany(
                '''
                insert into skill_achievements (skill_id, achievement_id) values (
                    (select skill_id from skills where name = ?), ?
                )
                ''',
                [(s.name, achievement_id,) for s in a.skills])
        except sqlite3.IntegrityError:
            pass

    for e in tree['education']:
        try:
            con.execute(
                '''
                insert into education (
                    institution, qualification, detail, start_date, end_date
                ) values (?, ?, ?, ?, ?)
                ''',
                        (e.institution, e.qualification, e.detail,
                         e.start_date if e.start_date else None,
                         e.end_date if e.end_date else None, ))
        except sqlite3.IntegrityError:
            pass

    for v in tree['versions']:
        try:
            cur = con.execute(
                '''
                insert into versions (name) values (?) returning version_id
                '''
                , (v.name, ))
            version_id = cur.fetchone()[0]
            con.executemany(
                '''
                insert into version_categories (version_id, category_id) values (
                    ?, (select category_id from categories where name = ?)
                )
                ''',
                [(version_id, c.name, ) for c in v.categories])
        except sqlite3.IntegrityError:
            pass

con.close()