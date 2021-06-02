from DP_PDS.sketches.pcsa import PCSA
import mmh3


class PrivSketch:
    """Class that can be used to execute the algorithm"""
    def __init__(self, epsilon, uniques, dp_var, sketch_var, sketch_dict, hash_function=mmh3):
        """
        Parameters
        ----------
        epsilon : double
            differential privacy guarantee. According to epsilon, prob1 and prob2
            are computed.
        uniques : string[]
            number of discrete quantitative categories
        dp_var: obj
            differentially private mechanism used
        sketch_var: obj 
            probabilistic data structure (sketch) used
        sketch_dict: dictionary
            contains the parameters for the sketch
        hash_function : class, optional
            class containing the hash() function used for the pcsa (default is mmh3)
        
        Raises
        ------
        AttributeError
            if epsilon < 0, dimension <= 1 or if hash_function doesn't contain hash(key) function
        """
        if not callable(getattr(hash_function, "hash", None)):
            raise AttributeError('hash function class needs to have an .hash(key) method')

        if epsilon < 0:
            raise AttributeError('epsilon has to be positive')

        if not len(uniques) > 0:
            raise AttributeError('size of uniques has to be bigger than 0')

        if epsilon == 0:
            print('WARN: Epsilon == 0: Results will be completely random')

        self.uniques = uniques
        self.sketch_var = sketch_var

        self.dp_mechanism = dp_var(epsilon, len(uniques))

        self.sketch = {new_list: [] for new_list in uniques}
        for unq in uniques:
            if sketch_var == PCSA:
                obje = sketch_var(hash_function,**sketch_dict)
            else:
                raise AttributeError('unknown sketch variant')

            self.sketch[unq] = obje

    def count_dp(self, idnr, category):
        """adds an element to the sketch
        Parameters
        ----------
        idnr: String
            unique id of user
        category: 
            reported value of user
        """
        element = self.dp_mechanism.dp(category, self.uniques)
        self.sketch[int(element)].add(idnr)

    def compare(self, real_freq):
        """can be used at the end to compare the real frequency with the estimated results (will be printed)"""
        n_counts = 0
        for cat in self.sketch:
            n_counts += self.sketch[cat].count()

        for cat in self.sketch:
            estimation = self.dp_mechanism.get_cardinality(self.sketch[cat].count(), n_counts)
            print(cat, real_freq[cat], estimation)

    def get_estimated_cardinality(self, category):
        """returns the estimated frequency for the given category"""
        n_counts = 0
        for cat in self.sketch:
            n_counts += self.sketch[cat].count()

        return self.dp_mechanism.get_cardinality(self.sketch[category].count(), n_counts)

    def union(self, sketches):
        """unions the given sketches"""
        return self.sketch_var.union(sketches)

