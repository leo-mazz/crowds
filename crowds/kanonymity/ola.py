from .lattice import make_lattice, Node
from .information_loss import prec_loss
from .utils import df_to_values, k_anonymity_check

import copy
import math
import logging

import pandas as pd

def _add_k_minimal(node, k_min_set):
    """ Add node to k-minimal set, removing all higher nodes in path to leaf """
    to_remove = []

    for old_node in k_min_set:
        if node.has_descendant(old_node):
            to_remove.append(old_node)

    for doomed in to_remove:
        k_min_set.remove(doomed)

    k_min_set.add(node)

def _check_kanonymity(df, node, k, max_sup):
    return k_anonymity_check(df, node.gen_rules.keys(), k, max_sup)

def _k_min(b_node, t_node, k, max_sup, k_min_set=set()):
    """ Core of OLA's operation: build k-minimal set with binary search in generalization
    strategies of lattice """
    lattice_lvls = make_lattice(b_node, t_node)
    h = len(lattice_lvls)

    if h > 2:
        # look halfway between top and bottom node
        h = math.floor(h/2)
        for n in lattice_lvls[h]:
            if n.suitable_tag == True:
                _k_min(b_node, n, k, max_sup, k_min_set)
            elif n.suitable_tag == False:
                _k_min(n, t_node, k, max_sup, k_min_set)
            elif n.is_suitable(k, max_sup):
                n.set_suitable()
                _k_min(b_node, n, k, max_sup, k_min_set)
            else:
                n.set_non_suitable()
                _k_min(n, t_node, k, max_sup, k_min_set)

    else: # special case of a 2-node lattice
        if b_node.suitable_tag == False:
            n = t_node
        # It's not possible to know that b_node is k_anonymous. Otherwise it would have been selected as top
        # But it's possible across different strategies! (e.g.: if root is k-anonymous)
        elif b_node.suitable_tag == True:
            n = b_node
        elif b_node.is_suitable(k, max_sup):
            b_node.set_suitable()
            n = b_node
        else:
            b_node.set_non_suitable()
            n = t_node

        if n.suitable_tag == True:
            _add_k_minimal(n, k_min_set)
        elif n.is_suitable(k, max_sup):
            n.set_suitable()
            _add_k_minimal(n, k_min_set)

    return k_min_set

def _make_release(df, qis, k):
    """ Finalize release by suppressing required records and producing some stats """
    records, qi_idx = df_to_values(df, qis)
    original_size = len(records)
    qi_values = lambda record: tuple([record[idx] for idx in qi_idx])

    eq_classes = {}
    release = []

    for r in records:
        qi_signature = qi_values(r)
        if qi_signature in eq_classes.keys():
            eq_classes[qi_signature].append(r)
        else:
            eq_classes[qi_signature] = [r]

    sup_ec = 0
    sup_rec = 0
    for val in eq_classes.values():
        if len(val) >= k:
            release += val
        else:
            sup_ec += 1
            sup_rec += len(val)

    stats = {
        'eq_classes_before_sup': len(eq_classes.keys()),
        'suppressed_classes': sup_ec,
        'suppressed_records': sup_rec,
        'perc_suppressed_records': round((sup_rec/original_size)*100, 2),
    }

    release = pd.DataFrame(release, columns=df.columns)
    return release, stats

def anonymize(df, generalization_rules, k=5, info_loss=prec_loss, max_sup=0):
    """ Execute OLA """
    logging.info('Building lattice...')
    b_node, t_node = Node.build_network(generalization_rules, df, _check_kanonymity)

    logging.info('Searching lattice...')

    k_min_nodes = _k_min(b_node, t_node, k, max_sup)

    if len(k_min_nodes) == 0:
        # This cannot happen if, as they should, all generalization rules bring values to indistinguishability
        logging.info('No strategy was found! Aborting.')
        return None

    visited_nodes, checked_nodes, num_suitable, num_non_suitable = b_node.lattice_stats
    logging.info(f"visited {visited_nodes} nodes, checked {checked_nodes} nodes")
    logging.info(f"num k {num_suitable} nodes, num not k {num_non_suitable} nodes")

    logging.info('Choosing optimal generalization strategy...')

    losses = [(info_loss(node), node) for node in k_min_nodes]
    optimal_loss, optimal_node = min(losses, key=lambda x: x[0])

    logging.info(f'Best loss ({optimal_loss}) was obtained with node {optimal_node}')

    release, release_stats = _make_release(optimal_node.apply_gen(), generalization_rules.keys(), k)

    logging.info('Done.')
    logging.info(release_stats)

    return [release, optimal_node.gen_state]


__all__ = ['anonymize']