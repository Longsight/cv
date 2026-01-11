import yaml
from enum import auto, StrEnum
from datetime import date

class Competency(StrEnum):
    RUSTY = auto()
    OKAY = auto()
    GOOD = auto()
    EXCELLENT = auto()

    def __str__(self):
        return f'{self.name}'.title()

    def __repr__(self):
        return f'{self.name}'.title()
    
    @classmethod
    def _missing_(cls, value):
        if value is None:
            value = 'Good'
        value = value.title()
        for member in cls:
            if member.value.title() == value:
                return member
        return Competency.GOOD
        
def competency_to_yaml(dumper, data):
    node = dumper.represent_scalar(u'!Competency', u'%s' % data)
    return node

def competency_from_yaml(loader, node):
    competency = str(loader.construct_scalar(node))
    return Competency(competency)

yaml.add_representer(Competency, competency_to_yaml)
yaml.add_constructor(u'!Competency', competency_from_yaml)

class Skill(yaml.YAMLObject):
    yaml_tag = u'!Skill'
    yaml_flow_style = True

    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.competency = Competency(kwargs['competency'])

    def __hash__(self):
        return hash((self.name, ))

    def __repr__(self):
        return "%s(name=%r, competency=%r)" % (
            self.__class__.__name__, self.name, self.competency)

class Category(yaml.YAMLObject):
    yaml_tag = u'!Category'
    yaml_flow_style = True

    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.skills = []

    def __hash__(self):
        return hash((self.name, ))

    def __repr__(self):
        return "%s(name=%r, skills=%r)" % (
            self.__class__.__name__, self.name, self.skills)

class Role(yaml.YAMLObject):
    yaml_tag = u'!Role'
    yaml_flow_style = False

    def __init__(self, **kwargs):
        self.employer = kwargs['employer']
        self.title = kwargs['title']
        self.location = kwargs['location']
        if kwargs['start_date']:
            self.start_date = date.fromisoformat(kwargs['start_date'])
        else:
            self.start_date = date.fromisoformat('1986-12-10')
        if kwargs['end_date']:
            self.end_date = date.fromisoformat(kwargs['end_date'])
        else:
            self.end_date = date.today()

    def __lt__(self, other):
        return self.start_date > other.start_date

    def __eq__(self, other):
        return self.employer == other.employer

    def __hash__(self):
        return hash((self.employer, ))

    def __repr__(self):
        return "%s(employer=%r, title=%r, location=%r, start_date=%r, end_date=%r)" % (
            self.__class__.__name__, self.employer, self.title,
            self.location, self.start_date, self.end_date
        )
    
class Education(yaml.YAMLObject):
    yaml_tag = u'!Education'
    yaml_flow_style = False

    def __init__(self, **kwargs):
        self.qualification = kwargs['qualification']
        self.detail = kwargs['detail']
        self.institution = kwargs['institution']
        self.start_date = date(kwargs['start_date'], 1, 1)
        self.end_date = date(kwargs['end_date'], 1, 1)

    def __lt__(self, other):
        return self.start_date > other.start_date

    def __eq__(self, other):
        return self.institution == other.institution

    def __hash__(self):
        return hash((self.institution, ))

    def __repr__(self):
        return "%s(qualification=%r, detail=%r, institution=%r, start_date=%r, end_date=%r)" % (
            self.__class__.__name__, self.qualification, self.detail,
            self.institution, self.start_date, self.end_date
        )

class Achievement(yaml.YAMLObject):
    yaml_tag = u'!Achievement'
    yaml_flow_style = True

    def __init__(self, **kwargs):
        self.detail = kwargs['detail']
        self.role = kwargs['role']
        self.skills = []

    def __hash__(self):
        return hash((self.detail, ))

    def __repr__(self):
        return "%s(detail=%r, skills=%r)" % (
            self.__class__.__name__, self.detail, self.skills)

class Version(yaml.YAMLObject):
    yaml_tag = u'!Version'
    yaml_flow_style = False

    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.categories = []

    def __hash__(self):
        return hash((self.name, ))

    def __repr__(self):
        return "%s(name=%r, categories=%r)" % (
            self.__class__.__name__, self.name, self.categories)
