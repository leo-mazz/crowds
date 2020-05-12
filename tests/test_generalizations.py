from kanon.generalizations import GenRule

def test_one_level_genrule():
    rule = GenRule([])
    assert rule.apply('any', 1) is None
