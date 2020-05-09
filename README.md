# Optimal Lattice Anonymization
This is an implementation of the algorithm described by El Emam, Khalet, et al. (2009) [1]. Given a dataset, an information loss function, and a set of generalization strategies, it writes to disk a *k*-anonymous version [2], obtained using the single-dimensional global recording model, i.e.: the same values will be mapped consistently to the same generalizations in the new dataset, and the generalization for each dimension will not overlap.

## Usage
To define a set of generalization rules:

```python
gen_rules = GeneralizationRules()

def custom_gen(value, gen_level):
    return 'value'

gen_rules.add('attr_name', custom_gen, max_level=1)
```

In order for the algorithm to work correctly, **the loss function needs to be monotonic**, i.e. non dicreasing for increasing generalization levels. Some information loss functions are provided in `information_loss.py`. It is also possible to define a custom generalization function (which must have the same signature as the following example):

```python
def loss_fn(gen_rules, gen_status):
    return 0.0
```

Then, to anonymize:

```python
ola.anonymize(csv_file, k=10, loss=loss_fn, generalizations=gen_rules)
```

## References
[1] El Emam, Khaled, et al. "A globally optimal k-anonymity method for the de-identification of health data." Journal of the American Medical Informatics Association 16.5 (2009): 670-682.

[2] Sweeney, Latanya. "k-anonymity: A model for protecting privacy." International Journal of Uncertainty, Fuzziness and Knowledge-Based Systems 10.05 (2002): 557-570.
