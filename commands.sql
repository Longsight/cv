-- select * from skills where rowid in (select skill from achievement_skills where achievement = 68);
-- select * from achievements where rowid = 68;
-- delete from achievement_skills;
-- insert into skills values ('Android');
-- select rowid, * from skills where rowid > 84;
-- insert into skill_categories VALUES
-- (85, (select rowid from categories where category = 'hardware')),
-- (86, (select rowid from categories where category = 'networking')),
-- (87, (select rowid from categories where category = 'monitoring')),
-- (88, (select rowid from categories where category = 'mobile'))
-- ;
-- select * from skills where skill = 'Flutter';
-- drop table achievements;
-- create table achievements(detail text unique);
-- delete from achievement_skills;
-- CREATE TABLE achievement_roles(achievement integer, role integer, foreign key(achievement) references achievements(rowid) on update cascade on delete cascade, foreign key(`role`) references roles(rowid) on update cascade on delete cascade);
-- delete from achievement_roles;

-- insert into skill_categories values (
--     (select rowid from skills where skill = 'Leadership'),
--     (select rowid from categories where category = 'management')
-- );

-- insert into skills values ('Testing');
-- insert into skill_categories VALUES
-- ((select rowid from skills where skill = 'Testing'), (select rowid from categories where category = 'dev'))
-- ;


-- select rowid, * from achievements where achievements.rowid not in
--     (select distinct achievement from achievement_skills);

-- select distinct detail from achievements join achievement_skills on achievements.rowid = achievement_skills.achievement
--     where achievement_skills.skill in
--         (select skill from skill_categories where category = 1);

-- delete from achievements;
-- delete from achievement_roles;
-- delete from achievement_skills;


-- select roles.employer, achievements.detail from achievements join achievement_skills
--     on achievements.rowid = achievement_skills.achievement
--     join skills on achievement_skills.skill = skills.rowid
--     join skill_categories on skills.rowid = skill_categories.skill
--     join categories on skill_categories.category = categories.rowid
--     join version_categories on categories.rowid = version_categories.category
--     join versions on version_categories.version = versions.rowid
--     join achievement_roles on achievements.rowid = achievement_roles.achievement
--     join roles on achievement_roles.role = roles.rowid
--     where versions.version = 'sysadmin' group by achievements.detail
--     order by roles.start desc, achievements.rowid asc;


-- select categories.category as c, skills.skill as s from categories join skill_categories on categories.rowid = skill_categories.category
-- join skills on skill_categories.skill = skills.rowid order by c asc, s asc;

select a.rowid as a_id, a.detail, skills.skill as s, null, null, null
                  from achievements as a
                  join achievement_skills on a_id = achievement_skills.achievement
                  join skills on achievement_skills.skill = skills.rowid
                  where a_id not in (select distinct rowid from achievement_roles)
                  order by a_id asc, s asc;