# crowds
crowds is a Python module that provides a suite of anonymization algorithms, allowing to transform [Pandas](https://pandas.pydata.org/) dataframes so that they satisfy *k*-anonymity or differential privacy. This is a **work in progress**. So far, one algorithm has been implemented (OLA). [Get in touch](mailto:leo@mazzone.space) if you would like to contribute.

## Optimal Lattice Anonymization
This is an implementation of the algorithm described by El Emam, Khalet, et al. (2009) [1]. Given a dataframe, an information loss function, and a set of generalization strategies, it returns a *k*-anonymous version [2], obtained using the single-dimensional global recording model, i.e.: the same values will be mapped consistently to the same generalizations in the new dataset, and the generalization for each dimension will not overlap.

### Usage
To define a set of generalization rules:

```python
from crowds.kanonymity.generalizations import GenRule

def first_gen(value):
    return 'value'

def second_gen(value):
    return 'value'

new_rule = GenRule([first_gen, second_gen])
ruleset = {
    'attr_name': new_rule,
}
```

In order for the algorithm to work correctly, **the loss function needs to be monotonic**, i.e. non-decreasing for increasing generalization levels. Some information loss functions are provided in `information_loss.py`. It is also possible to define a custom generalization function (which must have the same signature as the following example):

```python
def loss_fn(node):
    return 0.0
```

Then, to anonymize:

```python
from crowds.kanonymity import ola
anonymous_df = ola.anonymize(df, k=10, loss=loss_fn, generalizations=gen_rules)
```

For more, check out [this example](example/example.py), using the "Adult" dataset from the UCI Machine Learning Repository [3].

## References
[1] El Emam, Khaled, et al. "A globally optimal k-anonymity method for the de-identification of health data." Journal of the American Medical Informatics Association 16.5 (2009): 670-682.

[2] Sweeney, Latanya. "k-anonymity: A model for protecting privacy." International Journal of Uncertainty, Fuzziness and Knowledge-Based Systems 10.05 (2002): 557-570.

[3] Dua, D. and Graff, C. "UCI Machine Learning Repository." Irvine, CA: University of California, School of Information and Computer Science (2019). 
