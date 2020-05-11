import pandas as pd
from ola import anonymize
from information_loss import dm_star_loss
from generalizations import GenRule

column_names = [
    'age',
    'workClass',
    'fnlwgt',
    'education',
    'education-num',
    'marital-status',
    'occupation',
    'relationship',
    'race',
    'sex',
    'capital-gain',
    'capital-loss',
    'hours-per-week',
    'native-country',
    'income'
]

def generalize_age(value):
    if value <= 1950:
        return 'quite old'
    if value > 1950 and value <= 1980:
        return 'a bit old'
    if value > 1980 and value <= 2000:
        return 'young'
    if value > 2000:
        return 'too young'

generalization_rules = {
    'age': GenRule([generalize_age]), # 2-levels generalization
    'sex': GenRule([]), # 1-level generalization
}

adult = pd.read_csv('adult.csv', names=column_names, sep=' *, *', na_values='?', engine='python')
anonymize(adult, generalization_rules=generalization_rules, k=10, max_sup=0.5, info_loss=dm_star_loss)
