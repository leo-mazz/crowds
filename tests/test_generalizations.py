from kanon.generalizations import GenRule

import pytest


def custom_level_one(value):
    return value % 3 # maps everything to 0, 1, 2

def custom_level_two(value):
    return value % 2 # maps 0 and 2 to 0 and 1 to 1

def incomplete_level(value):
    if value % 3 == 0:
        return 0
    if value % 3 == 1:
        return 1

def test_one_level_genrule():
    rule = GenRule([])
    assert rule.apply('any', 0) == 'any'
    assert rule.apply('any', 1) is None


def test_custom_levels():
    rule = GenRule([custom_level_one, custom_level_two])
    assert rule.apply(11, 1) == 2
    assert rule.apply(2, 2) == 0

def test_verify_level():
    rule = GenRule([custom_level_one, custom_level_two])
    with pytest.raises(ValueError):
        rule.apply(8, 'level1')
    with pytest.raises(ValueError):
        rule.apply(8, -2)
    with pytest.raises(ValueError):
        rule.apply(8, 4) # 0 is identity, 1 and 2 are custom, 3 is map to None

def test_missing_coverage():
    rule = GenRule([incomplete_level])
    with pytest.raises(ValueError):
        rule.apply(8, 1)

def test_apply_level_equivalent():
    rule = GenRule([custom_level_one])
    assert rule.apply(12, 1) == rule.level(1)(12) != None
    assert rule.apply(13, 1) == rule.level(1)(13) != None