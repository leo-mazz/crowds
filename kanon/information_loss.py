from .utils import df_to_values

import math
from collections import defaultdict

def prec_loss(node):
    loss = 0
    for qi_name, qi_gen in node.gen_state.items():
        loss += (qi_gen / node.gen_rules[qi_name].max_level)

    return loss


def dm_star_loss(node):
    def equivalence_classes(release, q_ids):
        values = lambda entry: tuple([entry[idx] for idx in q_ids])

        eq_classes = {}
        for r in release:
            r_signature = values(r)
            if r_signature in eq_classes.keys():
                eq_classes[r_signature].append(r)
            else:
                eq_classes[r_signature] = [r]

        return eq_classes.values()

    release, qi_idx = df_to_values(node.apply_gen(), node.gen_rules.keys())
    e_classes = equivalence_classes(release, qi_idx)
    records_per_class = [len(ec) for ec in e_classes]
    loss = 0
    for ec_size in records_per_class:
        loss += ec_size**2

    return loss


def entropy_loss(node):
    records, q_ids = df_to_values(node.df, node.gen_rules.keys())
    release, q_ids = df_to_values(node.apply_gen(), node.gen_rules.keys())

    freq_a = {}
    freq_b = {}
    for q in q_ids:
        freq_a[q] = defaultdict(int)
        freq_b[q] = defaultdict(int)
        for a in records:
            freq_a[q][a[q]] += 1
        for b in release:
            freq_b[q][b[q]] += 1

    summation = 0
    for q in q_ids:
        for i, entry in enumerate(records):
            a = entry[q]
            b = release[i][q]
            summation += math.log2(freq_a[q][a] / freq_b[q][b])


    return -summation

__all__ = ['prec_loss', 'dm_star_loss', 'entropy_loss']