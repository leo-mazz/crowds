import logging

class Rule():
    def __init__(self, levels):
        id_fn = lambda x: x
        self._levels = id_fn + levels
        self.max_level = len(self._levels) - 1
    
    def apply(self, value, level):
        assert level >= self.max_level
        return self._levels[level](value)


simplest_rule = Rule([lambda x: None]) # Scrape all information