import math
from bitarray import bitarray
import mmh3
import numpy as np

class PCSA:
    """Class that implements Probabilistic Counting with sotchastic averaging (PCSA)
    It's a hash-based probabilistic algorithm for counting the number of distinct
    values in the presence of duplicates.

    Attributes
    ----------
    nmap : int
        amount of sketches in the bitmap
    length : int
        length of the sketches
    bitmap : bitarray[]
        array of bitarrays containing all of the information
    hash_function: class
         class containing the hash() function used for the pcsa
    PHI : double
        correction factor

    Methods
    -------
    sketch()
        returns the bitmap
    sizeof()
        returns theoretical size of bitmap
    add(item)
        adds new item to the bitmap
    count()
        estimates the number of unique elements in the sketches
    perturbSketches()
        perturb the sketches
    calculate_prop_factor()
        calculate the correction factor
    
    Reference
    ---------
        Flajolet, Philippe, and G. Nigel Martin. "Probabilistic counting
        algorithms for data base applications." Journal of computer and system
        sciences 31.2 (1985): 182-209.
    """

    def __init__(self,hash_function,nmap, length,r=0):
        """
        Parameters
        ----------
        nmap : int
            amount of sketches in the bitmap (at least one counter is required)
        length : int
            length of the sketches (should be at least 1)
        hash_function : class, optional
            class containing the hash() function used for the pcsa (default is mmh3)
        r : double, optional, default r=0 (no additional noise)
            perturbation factor (additional noise)

        Raises
        ------
        AttributeError
            if hash_function doesn't contain hash(key) function or nmap/length < 1
        """
        if nmap < 1 or length < 1:
            raise AttributeError('nmap and length have to be at least 1')

        if not callable(getattr(hash_function, "hash", None)):
            raise AttributeError('hash function class needs to have an .hash(key) method')

        self.hash_function = hash_function
        self.nmap = nmap
        self.length = length
        self.bitmap = [length * bitarray('0') for i in range(nmap)]
        self.r = r
        self.calculate_prop_factor() 
        if (self.r>0):
            self.perturbSketches()

    def __hash(self, key):
        """returns hash of the key using the hash function"""
        return self.hash_function.hash(key)

    def sketch(self):
        """returns the bitmap"""
        return self.bitmap

    def sizeof(self):
        """returns theoretical size of bitmap"""
        return (self.nmap * self.length) / 8

    def add(self, item):
        """Index the element into the bitmap using the hash function
        Parameters
        ----------
        item : obj
            The element to be indexed into the counter.
        """
        hashed_value = self.__hash(item)
        index_alpha = hashed_value % self.nmap
        ix = int(hashed_value / self.nmap)
        ix = bin(ix)[2:][::-1]

        index_beta = ix.find("1")  # find index of lsb
        if self.bitmap[index_alpha][index_beta] == 0:
            self.bitmap[index_alpha][index_beta] = 1

    def count(self):
        """Estimate the number of unique elements in the sketches.
        
        Note
        ----
        According to [1], the estimation of cardinality can be computed by
        averaging estimations from each sketch and converting the result value
        R into expected number of unique elements by the formula:
            card = nmap * 2^sum({R/nmap}) / 0.77351
        
        Note
        ----
        When R is small, the estimation leads to inaccuracies. 
        These can be mitigated to some extent by using a different estimation 
        method based on "hit counting" [2]. 
        As long as the fraction k of set bits (taking false positives into account)
        is below 30%, we consider the fraction of 0-bits at the first bit
        position of each sketch and calculate the cardinality as:
            card = (-2 * nmap) * log(k/nmap)

        References
        ----------
        [1] Flajolet, P., Martin, G.N.: Probabilistic Counting Algorithms
            for Data Base Applications. Journal of Computer and System Sciences.
            Vol. 31 (2), 182--209  (1985)
        [2] Lieven, P., Scheuermann, B.: High-Speed Per-Flow Traffic
            Measurement with Probabilistic Multiplicity Counting.
            In: INFOCOM. pp.1253-1261 (2010)
        """

        sum_one = 0
        for row in range(self.nmap):
            sum_one += self.bitmap[row][0]
        k = self.nmap - sum_one
        if k > 0.3 * self.nmap:  # hit counting; correction for small cardinalities
            a = float(k) / self.nmap
            cardinality = (-2.0 * self.nmap) * math.log(a)
            return cardinality
        else:
            sum_ix = 0
            for row in range(self.nmap):
                for col in range(self.length):
                    if self.bitmap[row][col] == 0:
                        sum_ix += col
                        break

            a = float(sum_ix) / self.nmap
            cardinality = self.nmap * (2 ** a) / self.PHI
            return cardinality

    def perturbSketches(self):
        """Perturb the sketch [1]. According to proportion r randomly set bits.
        
        Parameters
        ----------
        r: double
            probability to set an index of a bitmap counter

        References
        ----------
        [1]  Tschorsch, F., Scheuermann, B.: An algorithm for privacy-preserving
             distributeduser statistics. Computer Networks 57(14),
             2775–2787 (2013)
        """
        randmatrix = np.random.choice(a=[0, 1], size=(self.nmap, self.length), p=[1-self.r, self.r])
        for idx in range(self.nmap):
            self.bitmap[idx] = self.bitmap[idx] | bitarray(list(randmatrix[idx]))
	
    def calculate_prop_factor(self):
        """ calculate the correction factor depending on the perturbation r
        
        Parameters
        ----------
        r: double
            probability to set an index of a bitmap counter.
                
        Returns
        -------
        PHI : double
            correction factor.
        """
        if self.r == 0:
            self.PHI = 0.773519
        else:
            w = 32
            n = 100000
            qk = 1.0
            expected_value = 0
            a = 0
            for j in range(1, w + 1):
                for i in range(1, j + 1):
                    qk = qk * (1 - ((1 - (2 ** (-i))) ** n) * (1 - self.r))
                    qk1 = qk * (1 - ((1 - (2 ** (-(i + 1)))) ** n) * (1 - self.r))
                    a = qk - qk1
                qk = 1.0
                expected_value = expected_value + (j * a)
            propfac = (2 ** expected_value) / n
            self.PHI = propfac

    @staticmethod
    def union(pcsas):
        """ Unions all of the bitmaps contained in PCSA and returns the combined bitmap

        Note
        ----
        All bitmaps need to have the same values for nmap, length and hash_function

        Raises
        ------
        AttributeError
            if nmap, length or hash_function differs between at least two bitmaps
        """
        nmap = pcsas[0].nmap
        length = pcsas[0].length
        hash_fct = pcsas[0].hash_function
        union = PCSA(hash_fct,nmap, length)
        for pcsa_idx in range(0, len(pcsas)):
            pcsa_sketch = pcsas[pcsa_idx]
            if nmap != pcsa_sketch.nmap:
                raise AttributeError('sketches have different values for nmap')
            if pcsa_sketch.length != length:
                raise AttributeError('sketches have different values for length')
            if pcsa_sketch.hash_function != hash_fct:
                raise AttributeError('pcsa objects use different hash functions')
            for sketch_idx in range(pcsa_sketch.nmap):
                union.bitmap[sketch_idx] = union.bitmap[sketch_idx] | pcsa_sketch.bitmap[sketch_idx]
        return union
