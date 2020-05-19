def df_to_values(df, quasi_identifiers):
    records = df.values
    qi_indices = [list(df.columns).index(qi) for qi in quasi_identifiers]

    return records, qi_indices

def k_anonymity_check(df, quasi_identifiers, k, max_sup=0):
        records, qi_indices = df_to_values(df, quasi_identifiers)
        # Using simple dict instead of 'collections' library: much better space requirements for Python > 3.6
        qi_values = lambda record: tuple([record[idx] for idx in qi_indices])
        eq_classes = {}

        max_sup = int(len(records) * max_sup / 100)

        for r in records:
            qi_signature = qi_values(r)
            if qi_signature in eq_classes.keys():
                eq_classes[qi_signature] +=1
            else:
                eq_classes[qi_signature] = 1

        for val in eq_classes.values():
            if val < k:
                if max_sup < val:
                    return False
                else:
                    max_sup -= val

        return True



__all__ = ['df_to_values', 'k_anonymity_check']