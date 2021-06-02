# DP-PDS: Differentially Private Probabilistic Data Structures

This package provides a generalization of RRTxFM [1] by combining cardinality estimators with differentially private mechanisms.
RRTxFM is an FM Sketch with differential privacy guarantee by applying the randomized response technique.
For a detailed description of the algorithm, see the [paper](https://eprint.iacr.org/2019/805.pdf).

## Contact
For further questions, please contact `saskia.nunezvonvoigt[at]tu-berlin.de`.

## Installation
To use the package, first the [GitHub repo](https://github.com/sanun/DP-PDS.git) needs to be cloned. 

To run the code the python packages mmh3, bitarray, math, random, and copy need to be installed.

## Usage

### Step 1: Initialization of the private-sketch
The PrivSketch class combines the functionality of the probabilistic data structure and the differential privacy mechanism. All necessary information will be passed to the constructor.

```python
from DP_PDS.priv_sketch import PrivSketch
```
The PrivSketch class needs the following parameters:
* epsilon (double): differential privacy guarantee
* uniques (string[]): number of discrete quantitative categories of the dataset
* dp_var (class): differentially private mechanism used
* sketch_var (class): probabilistic data structure (sketch) used
* sketch_dict (dictionary): contains the parameters for the sketch
* hash_function (class, optional): class containing the hash() function used for the pcsa (default is mmh3)

To use the package with the provided RRT and PCSA/FM-Sketches the following imports are needed:

```python
from DP_PDS.sketches.pcsa import PCSA
from DP_PDS.dp.rrt import RRT
```
Then the parameters for the PCSA object need to be provided in the sketch_dict.
Nmap and length are the parameters that are necessary for the initialization of the PCSA object/FM-Sketches. Nmap defines the amount of sketches and length defines the length of each sketch 

In the example the hash function doesn't need to be set necessarily because the mmh3 hash function is set by default.

```python
sketch_dict = {'nmap': 256, 'length': 32}
private_sketch = PrivSketch(epsilon=1.0, uniques=uniques, dp_var=RRT, sketch_dict=sketch_dict,sketch_var=PCSA, hash_function=mmh3)
```

### Step 2: Add values to the sketch

First the dataset on which the algorithm should be performed needs to be loaded (e.g. with the Pandas package) and decided which category of the dataset should be used together with the mandatory column containing unique ids for each entry. Additionally the list of unique elements need to be detected.

Code Example:
```python
private_sketch.count_dp('alice', 'bachelor')
```

In this example the element 'alice' will be added to the category 'bachelor' with a certain probability depending on the epsilon set in the initialisation.

### Step 3: Get cardinality

After the filling of the sketches is complete, the estimated cardinality of the individual categories can be retrieved by using the get_estimated_cardinality() function.

Example for retrieving the estimated cardinality of the bachelor category:
```python
card = private_sketch.get_estimated_cardinality('bachelor')
```
Additionally it is possible print out a comparison of all estimated values in comparison with the real values by using the compare() function which expects a dict that contains the real frequency for all categories given to the constructor (uniques):
```python
private_sketch.compare(real_freq)
```

### Specific execution example

For a better understanding of the package a full example will be given.

The following dataset is contained in the package and will be used for this example(adult_mod_encoded.csv): https://archive.ics.uci.edu/ml/datasets/Adult. The dataset was already extended by a column containing unique ids.

The following imports a needed:
```python
import pandas as pd
import numpy as np
from DP_PDS.sketches.pcsa import PCSA
from DP_PDS.dp.rrt import GRR
from DP_PDS.priv_sketch import PrivSketch
import mmh3
```

First the category that should be used will be selected, the dataset will be loaded, and the real frequencies will be stored. (The caseid column contains the unique ids):
```python
cat_col = 'workclass'
df = pd.read_csv('adult_mod_encoded.csv', usecols=['caseid', cat_col], low_memory=False)
real_freq = dict(df[cat_col].value_counts())
```

Afterwards uniques and sketch_dict will be set to initialize the private_sketch:
```python
uniques = list(np.unique(df[cat_col]))
sketch_dict = {'nmap': 256, 'length': 32}
private_sketch = PrivSketch(epsilon=1.0, uniques=uniques, dp_var=RRT, sketch_dict=sketch_dict, sketch_var=PCSA, hash_function=mmh3)
```

To end the execution the FM-Sketches will be filled and afterwards the comparison of the real and the estimated frequencies will be printed out:
```python
for i in range(len(df[cat_col])):
    private_sketch.count_dp(df.loc[i, 'caseid'], df.loc[i, cat_col])
private_sketch.compare(real_freq)
```

### Merging sketches

The PrivSketch class also enables the possibility to merge multiple sketches if the class of the according probabilistic data structure implements an union function as well.

After the execution of the algorithm the filled sketches can be easily combined:
```python
sketchesunion = private_sketch.union(private_sketch.sketch)
```
In this example all of the sketches are combined but it is also possible to combine just some specific by passing them to the function in an array.
```python
sketchesunion = private_sketch.union(list(private_sketch.sketch.values())[:2])
```

## Extension of the Implementation

The implementation can be easily extended by importing other classes and passing them to the priv_sketch constructor.

1. Hash function: Another hash function can be used by importing the class and pass it to the constructor for the hash_function parameter. The only requirement for the class is that it should have a hash(key) function.


2. Differential privacy mechanism: Another DP mechanism can be used by importing the class and pass it to the constructor for the dp_var parameter. The according object will be initialized using the parameters epsilon and len(uniques). The class is required to have a dp(element, uniques) function that executes the DP mechanism and a get_cardinality(card, n) function that returns the unbiased cardinality.


3. Probabilistic data structure: An other probabilistic data structure can be used by importing the class and pass it to the constructor for the hash_function parameter together with all necessary parameters defined in the sketch_dict variable. The class is required to have an add(element) function to add new elements to the sketches and a count() function that will be used to estimate the number of unique elements in the sketches. Optionally, if this functionality is needed, a union(sketch_list) function should be contained which unions the sketches passed in the sketch_list.
Additionally a small extension in the PrivSketch class is necessary:

As an example the HyperLogLog class from https://github.com/gakhov/pdsa will be used because it implements all necessary functionality (besides the union):

```python
from pdsa.cardinality.hyperloglog import HyperLogLog
...
sketch_dict = {'precision': 8}
private_sketch = PrivSketch(epsilon=1.0, uniques=uniques, dp_var=rrt.RRT, sketch_dict=sketch_dict, sketch_var=HyperLogLog)
```

The only parameter needed for the initialization of the HyperLogLog class is the precision

Extension in the priv_sketch.py:

```python
from pdsa.cardinality.hyperloglog import HyperLogLog
...
for unq in uniques:
    if sketch_var == pcsa.PCSA:
        obje = sketch_var(hash_function,**sketch_dict)
    elif sketch_var == HyperLogLog:
        obje = sketch_var(sketch_dict['precision']) 
```

Only the last two lines of the example had to be added to enable the usage of the HyperLogLog class together with RRT as the DP mechanism.

## Papers
[1] Nuñez von Voigt S., Tschorsch F. (2020) RRTxFM: Probabilistic Counting for Differentially Private Statistics. In: Pappas I., Mikalef P., Dwivedi Y., Jaccheri L., Krogstie J., Mäntymäki M. (eds) Digital Transformation for a Sustainable Society in the 21st Century. I3E 2019. IFIP Advances in Information and Communication Technology, vol 573. Springer, Cham. https://doi.org/10.1007/978-3-030-39634-3_9

## Thanks
Thanks to Florian Kögel for his contribution to the prototype implementation.
