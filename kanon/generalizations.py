class GenRule():
    def __init__(self, levels):
        id_fn = lambda x: x
        none_fn = lambda x: None
        self._levels = [id_fn] + levels + [none_fn]
        self.max_level = len(self._levels) - 1

    def _verify_level(self, level):
        if level < 0 or level > self.max_level:
            raise ValueError('Not enough generalization steps available with this rule')
    
    def apply(self, value, level):
        self._verify_level(level)
        return self._levels[level](value)

    def level(self, lvl):
        self._verify_level(lvl)
        return self._levels[lvl]