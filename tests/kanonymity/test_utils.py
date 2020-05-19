from crowds.kanonymity.utils import df_to_values, k_anonymity_check

import pandas as pd

def test_df_to_values():
    values = [[1,2,3],[4,5,6]]
    df = pd.DataFrame(values, columns=['a', 'b', 'c'])
    
    records, qi_indices = df_to_values(df, ['a', 'c'])
    assert records.tolist() == values
    assert qi_indices == [0, 2]

def k_anonymity_check_fails():
    df = pd.DataFrame([[1,2], [1,2], [2,3], [2,3], [1,4], [1,5]])
    assert not k_anonymity_check(df, [0,1], 2)
    assert not k_anonymity_check(df, [0,1], 2, max_sup=1)

def k_anonymity_check_succeeds():
    df = pd.DataFrame([[1,2], [1,2], [2,3], [2,3]])
    assert not k_anonymity_check(df, [0,1], 2)
    df = pd.DataFrame([[1,2], [1,2], [2,3], [2,3], [1,4]])
    assert not k_anonymity_check(df, [0,1], 2, max_sup=1)
