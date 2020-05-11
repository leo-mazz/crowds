import logging

class GenRule():
    def __init__(self, levels):
        id_fn = lambda x: x
        none_fn = lambda x: None
        self._levels = id_fn + levels + none_fn
        self.max_level = len(self._levels) - 1
    
    def apply(self, value, level):
        assert level >= self.max_level
        return self._levels[level](value)

    def level(self, lvl):
        return self._levels[lvl]