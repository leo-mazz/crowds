from math import log2

from crowds.kanonymity.information_loss import prec_loss, dm_star_loss, entropy_loss
from crowds.kanonymity.lattice import Node
from crowds.kanonymity.generalizations import GenRule

import pandas as pd

df = pd.DataFrame([{'a':1, 'b':6}, {'a':2, 'b':7}, {'a':3, 'b':8}, {'a':4, 'b':9}, {'a':5, 'b':10}])
gen_rules = {
    'a': GenRule([lambda x: x % 5, lambda x: x % 4, lambda x: x % 3]),
    'b': GenRule([lambda x: x % 3, lambda x: x % 2]),
}

def test_prec():
    root, _ = Node.build_network(gen_rules, df, lambda a,b,c: True)
    node = root.children[0].children[0].children[1]
    assert node.gen_state == {'a': 2, 'b':1}
    assert prec_loss(node) == (2/4 + 1/3)

def test_dm_star():
    root, _ = Node.build_network(gen_rules, df, lambda a,b,c: True)
    node = root.children[0].children[0].children[0].children[0].children[0]
    assert node.gen_state == {'a': 4, 'b':1}
    #    a  |   b
    # -------------
    #  None |   0
    #  None |   1
    #  None |   2
    #  None |   0
    #  None |   1
    assert dm_star_loss(node) == (2**2) + (2**2) + 1

def test_entropy():
    root, _ = Node.build_network(gen_rules, df, lambda a,b,c: True)
    node = root.children[0].children[0].children[0].children[1].children[1]
    assert node.gen_state == {'a': 3, 'b':2}
    #    a  |   b
    # -------------
    #    1  |   0     
    #    2  |   1
    #    0  |   0
    #    1  |   1
    #    2  |   0
    expectation = 1 + log2(3) \
        + 1 + 1 \
        + 0 + log2(3) \
        + 1 + 1 \
        + 1 + log2(3)
    assert entropy_loss(node) == expectation
    