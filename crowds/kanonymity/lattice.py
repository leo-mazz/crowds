import copy
import logging

def _validate_gen_state(state):
    assert isinstance(state, dict)

    for k in state.keys():
        if not isinstance(k, str):
            raise ValueError('The keys in a generalization state should be strings')
    for v in state.values():
        if not isinstance(v, int) or v < 0:
            raise ValueError('The values in a generalization state should be non-negative integers')
    

class Node():
    def __init__(self, gen_state, root=None):
        if root == None:
            if len(set(gen_state.values())) > 1 or list(gen_state.values())[0] != 0:
                raise ValueError('Root node cannot have intermediate generalization state')
            self._root = self
        else:
            self._root = root

        _validate_gen_state(gen_state)
        self.gen_state = gen_state

        self.children = []
        self.parents = []
        self._suitable_tag = None
    
    def __repr__(self):
        state = self.gen_state.__repr__()
        if self._root == self:
            return 'ROOT node{}'.format(state)
        else:
            return 'node{}'.format(state)
    
    @classmethod
    def build_network(cls, rules, df, suitable_check, suitable_upwards=True):
        init_state = {qi: 0 for qi in rules.keys()}
        b_node = cls(init_state)
        b_node.visited_nodes = 0
        b_node.checked_nodes = 0
        b_node.num_suitable = 0
        b_node.num_non_suitable = 0
        b_node.all_states = {}
        b_node.rules = rules
        b_node.suitable_check = suitable_check
        b_node.suitable_upwards = suitable_upwards
        b_node._df = df
        b_node._make_children()

        t_node = b_node
        # there is only one node in the last level
        while len(t_node.children) > 0:
            t_node = t_node.children[0]

        return b_node, t_node

    def _make_children(self):
        for qi, level in self.gen_state.items():
            if level < self.gen_rules[qi].max_level:
                new_state = copy.deepcopy(self.gen_state)
                new_state[qi] = level + 1
                tuple_new_state = tuple(new_state.items())
                if tuple_new_state not in self._root.all_states.keys():
                    child = Node(new_state, self._root)
                    child.parents.append(self)
                    self._root.all_states[tuple_new_state] = child
                    self.children.append(child)
                    child._make_children()
                else:
                    child = self._root.all_states[tuple_new_state]
                    self.children.append(child)
                    child.parents.append(self)

    def _is_in_path(self, b_node, t_node, strict=False):
        if strict and (self == b_node):
            return False

        for qi, level in self.gen_state.items():
            if level < b_node.gen_state[qi] or level > t_node.gen_state[qi]:
                return False

        return True

    def has_descendant(self, node):
        return node._is_in_path(self, self.leaf, strict=True)

    def set_suitable(self):
        self._suitable_tag = True
        self._root.visited_nodes += 1
        self._root.num_suitable += 1
        # In the case of k-anonymity, if a node is suitable so will all of its children
        # Information loss works in reverse
        propagate = self.children if self._root.suitable_upwards else self.parents
        for c in propagate:
            if c.suitable_tag == None:
                c.set_suitable()

    def set_non_suitable(self):
        self._suitable_tag = False
        self._root.visited_nodes += 1
        self._root.num_non_suitable += 1
        # In the case of k-anonymity, if a node is not suitable nor will all of its parents
        # Information loss works in reverse
        propagate = self.parents if self._root.suitable_upwards else self.children
        for p in propagate:
            if p.suitable_tag == None:
                p.set_non_suitable()

    @property
    def gen_rules(self):
        return self._root.rules
    
    @property
    def lattice_stats(self):
        return {
            'visited_nodes': self._root.visited_nodes,
            'checked_nodes': self._root.checked_nodes,
            'num_suitable': self._root.num_suitable,
            'num_non_suitable': self._root.num_non_suitable,
        }
    
    @property
    def df(self):
        return self._root._df
    
    @property
    def leaf(self):
        if len(self.children) == 0:
            return self
        else:
            return self.children[0].leaf

    @property
    def suitable_tag(self):
        return(self._suitable_tag)

    @property
    def is_root(self):
        return self._root == self

    def is_suitable(self, value, max_sup=None):
        self._root.checked_nodes += 1
        release = self.apply_gen()
        if max_sup is None:
            return self._root.suitable_check(release, self, value)
        return self._root.suitable_check(release, self, value, max_sup)        

    def apply_gen(self):
        gen_df = self.df.copy()

        for col, gen_level in self.gen_state.items():
            gen_df[col] = gen_df[col].apply(
                self.gen_rules[col].level(gen_level))

        return gen_df

def make_lattice(b_node, t_node):
    lattice = [[b_node]]

    while True:
        prev_level = lattice[-1]
        this_level = set()
        for node in prev_level:
            for child in node.children:
                if child._is_in_path(b_node, t_node):
                    this_level.add(child)
        lattice.append(list(this_level))

        if len(lattice[-1]) == 1 and lattice[-1][0] == t_node:
            return lattice

__all__ = ['Node', 'make_lattice']