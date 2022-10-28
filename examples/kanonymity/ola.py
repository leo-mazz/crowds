import pandas as pd
from crowds.kanonymity.ola import anonymize
from crowds.kanonymity.information_loss import dm_star_loss
from crowds.kanonymity.generalizations import GenRule

# Globally pandas printing options: Show all columns and rows if displaying tables.
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
# Prevent line breaks of rows
pd.set_option('display.expand_frame_repr', False)

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
    if value > 60:
        return 'quite old'
    if value > 35 and value <= 60:
        return 'a bit old'
    if value > 20 and value <= 35:
        return 'young'
    if value <= 20:
        return 'too young'

generalization_rules = {
    'age': GenRule([generalize_age]), # 2-levels generalization
    'sex': GenRule([]), # 1-level generalization
}

adult = pd.read_csv('../adult.csv', names=column_names, sep=' *, *', na_values='?', engine='python')
adult_anonymized, transformation = anonymize(adult, generalization_rules=generalization_rules, k=10, max_sup=0.0, info_loss=dm_star_loss)
print(adult_anonymized.head())
