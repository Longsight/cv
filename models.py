import yaml
from enum import auto, StrEnum

class Competency(StrEnum):
    POOR = auto()
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
        value = value.lower()
        for member in cls:
            if member.value.lower() == value:
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

    def __init__(self, name, competency):
        self.name = name
        self.competency = Competency(competency)

    def __repr__(self):
        return "%s(name=%r, competency=%r)" % (
            self.__class__.__name__, self.name, self.competency)

    @classmethod
    def to_yaml(cls, dumper, data):
        node = dumper.represent_mapping(u'!Skill', vars(data), flow_style=True)
        return node

class Category(yaml.YAMLObject):
    yaml_tag = u'!Category'

    def __init__(self, name):
        self.name = name
        self.skills = []

    def __repr__(self):
        return "%s(name=%r, skills=%r)" % (
            self.__class__.__name__, self.name, self.skills)
    
    @classmethod
    def to_yaml(cls, dumper, data):
        node = dumper.represent_mapping(u'!Category', vars(data), flow_style=True)
        return node

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

    @classmethod
    def to_yaml(cls, dumper, data):
        node = dumper.represent_mapping(u'!Role', vars(data), flow_style=True)
        return node
    