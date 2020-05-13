def df_to_values(df, quasi_identifiers):
    records = df.values
    qi_indices = [list(df.columns).index(qi) for qi in quasi_identifiers]

    return records, qi_indices


__all__ = ['df_to_values']