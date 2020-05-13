from kanon.lattice import Node, make_lattice
from kanon.generalizations import GenRule

import pytest
import pandas as pd

gen_state_root = {'a': 0, 'b': 0}
gen_state = {'a': 0, 'b': 1}
gen_rules = {
    'a': GenRule([lambda x: x % 2]),
    'b': GenRule([]),
}
df = pd.DataFrame([{'a':1, 'b':3}, {'a':2, 'b':4}])
suitable_check = lambda release, node, k: True

def test_check_root_state():
    with pytest.raises(ValueError):
        Node(gen_state)
    root = Node(gen_state_root)
    assert root.is_root
    node = Node(gen_state, root=root)
    assert not node.is_root

def test_valid_gen_state():
    root = Node(gen_state_root)
    with pytest.raises(ValueError):
        Node({'a': '1', 'b': '3'}, root=root)
    with pytest.raises(ValueError):
        Node({1: 1, 3: 3}, root=root)
    with pytest.raises(ValueError):
        Node({'a': 0, 'b': -1}, root=root)

def test_build_network():
    root, leaf = Node.build_network(gen_rules, df, suitable_check)
    # Network metadata
    assert gen_state_root == root.gen_state
    # assert root.visited_nodes == 0
    # assert root.checked_nodes == 0
    # assert root.num_suitable == 0
    # assert root.num_not_suitable == 0
    assert leaf != root
    assert id(leaf.df) == id(root.df)
    assert id(leaf.gen_rules) == id(root.gen_rules)

    # Network topology
    #    a2b1     |  LEAF
    #  a2b0 a1b1  |  2-steps
    #  a1b0 a0b1  |  1-step
    #    a0b0     |  ROOT
    assert root.parents == []
    assert len(root.children) == 2
    a1b0, a0b1 = root.children

    assert a1b0.parents == a0b1.parents == [root]
    assert len(a1b0.children) == 2
    assert len(a0b1.children) == 1
    a2b0, a1b1 = a1b0.children
    assert a1b1 == a0b1.children[0]

    assert a2b0.parents == [a1b0]
    assert a1b1.parents == [a1b0, a0b1]
    assert a2b0.children == a1b1.children == [leaf]

    leaf.parents == [a1b1, a2b0]
    leaf.children == []

    assert root.gen_state == {'a':0, 'b': 0}
    assert a1b0.gen_state == {'a':1, 'b': 0}
    assert a0b1.gen_state == {'a':0, 'b': 1}
    assert a2b0.gen_state == {'a':2, 'b': 0}
    assert a1b1.gen_state == {'a':1, 'b': 1}
    assert leaf.gen_state == {'a':2, 'b': 1}

def test_leaf():
    root, leaf = Node.build_network(gen_rules, df, suitable_check)
    assert leaf == root.leaf == root.children[0].leaf

def test_descendant():
    root, leaf = Node.build_network(gen_rules, df, suitable_check)

    assert not root.has_descendant(root)
    assert root.has_descendant(root.children[0])
    assert root.has_descendant(leaf)
    assert not leaf.has_descendant(root)

def test_suitability_check():
    root, leaf = Node.build_network(gen_rules, df, suitable_check)
    assert root.lattice_stats['checked_nodes'] == 0

    assert leaf.is_suitable(10)
    assert root.lattice_stats['checked_nodes'] == 1

def test_suitability_propagation():
    all_suitable = lambda ns: all([n.suitable_tag for n in ns])
    none_suitable = lambda ns: sum([n.suitable_tag for n in ns]) == 0

    root, leaf = Node.build_network(gen_rules, df, suitable_check)
    assert root.lattice_stats['visited_nodes'] == 0
    assert root.lattice_stats['num_suitable'] == 0
    assert root.lattice_stats['num_non_suitable'] == 0

    root.children[0].set_suitable()
    assert root.suitable_tag == None
    assert root.children[1].suitable_tag == None
    assert root.lattice_stats['visited_nodes'] == 4
    assert root.lattice_stats['num_suitable'] == 4
    assert root.lattice_stats['num_non_suitable'] == 0

    root.children[1].set_non_suitable()
    assert none_suitable([
        root.children[1],
        root
    ])
    assert all_suitable([
        root.children[0],
        root.children[0].children[0],
        root.children[0].children[1],
        leaf
    ])
    assert root.lattice_stats['visited_nodes'] == 6
    assert root.lattice_stats['num_suitable'] == 4
    assert root.lattice_stats['num_non_suitable'] == 2

def test_apply_gen():
    root, _ = Node.build_network(gen_rules, df, suitable_check)
    a1b1 = root.children[0].children[1]
    assert a1b1.gen_state == {'a':1, 'b':1}
    assert a1b1.apply_gen().values.T.tolist() == [[1,0], [None, None]]

def test_make_lattice():
    root, leaf = Node.build_network(gen_rules, df, suitable_check)
    lattice = make_lattice(root, leaf)
    assert len(lattice) == 4
    assert lattice[0] == [root]
    a1b0, a0b1, a2b0, a1b1 = [
        {'a':1, 'b': 0},
        {'a':0, 'b': 1},
        {'a':2, 'b': 0},
        {'a':1, 'b': 1}
    ]

    lattice1 = [n.gen_state for n in lattice[1]]
    assert (a1b0 in lattice1) and (a0b1 in lattice1)
    lattice2 = [n.gen_state for n in lattice[2]]
    assert (a1b1 in lattice2) and (a2b0 in lattice2)
    assert lattice[-1] == [leaf]
