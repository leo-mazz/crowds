import copy

class Node():
    def __init__(self, gen_state, root=None):
        self.gen_state = gen_state
        if root == None:
            self.root = self
        else:
            self.root = root

        self.children = []
        self.parents = []
        self._suitable_tag = None
    
    @classmethod
    def build_network(cls, rules, records, suitable_check, suitable_upwards=True, logger=None):
        init_state = {qi: 0 for qi in rules.keys()}
        b_node = cls(init_state)
        b_node.visited_nodes = 0
        b_node.checked_nodes = 0
        b_node.num_suitable = 0
        b_node.num_not_suitable = 0
        b_node.all_states = {}
        b_node.rules = rules
        b_node.suitable_check = suitable_check
        b_node.suitable_upwards = suitable_upwards
        b_node.records = records
        if logger != None:
            b_node.set_logger(logger)
        b_node.make_children()

        t_node = b_node
        # there is only one node in the last level
        while len(t_node.children) > 0:
            t_node = t_node.children[0]

        return b_node, t_node

    def __repr__(self):
        state = self.gen_state.__repr__()
        if self.root == self:
            return 'ROOT node{}'.format(state)
        else:
            return 'node{}'.format(state)

    def set_logger(self, logger):
        self.root.print = logger.print

    def make_children(self):
        for qi, level in self.gen_state.items():
            if level < self.root.rules[qi].max_level:
                new_state = copy.deepcopy(self.gen_state)
                new_state[qi] = level + 1
                tuple_new_state = tuple(new_state.items())
                if tuple_new_state not in self.root.all_states.keys():
                    child = Node(new_state, self.root)
                    child.parents.append(self)
                    self.root.all_states[tuple_new_state] = child
                    self.children.append(child)
                    child.make_children()
                else:
                    child = self.root.all_states[tuple_new_state]
                    self.children.append(child)
                    child.parents.append(self)

    def is_in_path(self, b_node, t_node, not_root=False):
        if not_root and self == b_node:
            return False

        for qi, level in self.gen_state.items():
            if level < b_node.gen_state[qi] or level > t_node.gen_state[qi]:
                return False

        return True

    def has_descendant(self, node):
        return node.is_in_path(self, self.leaf, not_root=True)

    def set_suitable(self):
        self._suitable_tag = True
        self.root.visited_nodes += 1
        self.root.num_suitable += 1
        # In the case of k-anonymity, if a node is suitable so will all of its children
        # Information loss works in reverse
        propagate = self.children if self.root.suitable_upwards else self.parents
        for c in propagate:
            if c.suitable_tag == None:
                c.set_suitable()

    def set_non_suitable(self):
        self._suitable_tag = False
        self.root.visited_nodes += 1
        self.root.num_not_suitable += 1
        # In the case of k-anonymity, if a node is not suitable nor will all of its parents
        # Information loss works in reverse
        propagate = self.parents if self.root.suitable_upwards else self.children
        for p in propagate:
            if p.suitable_tag == None:
                p.set_non_suitable()
    
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
        return self.root == self

    def is_suitable(self, value, max_sup=None):
        self.root.checked_nodes += 1
        self.root.print('Trying strategy {}'.format(self))
        self.root.print('Simulating release')
        release = self.apply_gen()
        if max_sup is None:
            return self.root.suitable_check(release, self, value)
        return self.root.suitable_check(release, self, value, max_sup)        

    def apply_gen(self):
        # return data_transform.apply_gen(self.root.records, self.gen_state, self.root.rules)
        gen_records = copy.deepcopy(self.root.records)
        for r in gen_records:
            for col, gen_level in self.gen_state.items():
                r[col] = self.root.rules[col].apply(r[col], gen_level)

        return gen_records
        


def make_lattice(b_node, t_node):
    lattice = [[b_node]]

    while True:
        prev_level = lattice[-1]
        this_level = set()
        for node in prev_level:
            for child in node.children:
                if child.is_in_path(b_node, t_node):
                    this_level.add(child)
        lattice.append(list(this_level))

        if len(lattice[-1]) == 1 and lattice[-1][0] == t_node:
            return lattice