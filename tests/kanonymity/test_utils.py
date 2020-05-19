from crowds.kanonymity.utils import df_to_values

import pandas as pd

def test_df_to_values():
    values = [[1,2,3],[4,5,6]]
    df = pd.DataFrame(values, columns=['a', 'b', 'c'])
    
    records, qi_indices = df_to_values(df, ['a', 'c'])
    assert records.tolist() == values
    assert qi_indices == [0, 2]