"""Variants of Randomized Response"""
import random
import math
import copy


class RRT:
    """ 
    Randomized Response Forced Model. With probability prob1 the true value is
    reported, with probability prob2 a forced (randomly selected of possible
    values) is reported.

    Attributes
    ----------
    epsilon : double
        differential privacy guarantee. According to epsilon, prob1 and prob2
        are computed.
    dimension : int
        number of discrete quantitative categories
    prob1 : double
        probability to report true value.
    prob2: double
        probability to report a forced (one of the possible) value.

    Methods
    -------
    get_probabilities()
        returns prob1 and prob2
    get_cardinality(card, n)
        returns the unbiased estimated cardinality
    rrt(element, uniques)
        returns the reported value (true or forced).
    
    Reference
    ---------
        Boruch, R. F (1971). Assuring confidentiality of responses in social
        research: a note on strategies. The American Sociologist, 6, 308–311.
   
    """
    def __init__(self, epsilon, dimension):
        """
        Parameters
        ----------
        epsilon : double
            differential privacy guarantee. According to epsilon, prob1 and prob2 
            are computed.
        dimension : int
            number of discrete quantitative categories (has to bigger than 1)

        Raises
        ------
        AttributeError
            if epsilon < 0 or dimension <= 1
        """
        if epsilon < 0:
            raise AttributeError('epsilon has to be positive')

        if dimension <= 1:
            raise AttributeError('dimension has to be bigger than 1')

        if epsilon == 0:
            print('WARN: Epsilon == 0: Results will be completely random')

        self.epsilon = epsilon
        self.dimension = dimension
        self.prob2 = 1/self.dimension
        self.prob1 = (math.exp(epsilon)-1) / (math.exp(epsilon) + self.dimension-1)

    def get_probabilities(self):
        """" 
        Returns
        -------
        prob1: double
            probability to report true value.
        prob2: double
            probability to report a forced (one of the possible) value.
        """
        return self.prob1, self.prob2
        
    def get_cardinality(self, card, n):
        """ Unbiased cardinality 
        Parameters
        ----------
        card: int
            Biased number of unique elements for one category.
        n: int
            Total number of elements (sum of cardinality of all categories). 
        
        Returns
        -------
        cardinality : int
            The unbiased cardinality. Corrected with probabilities and biased
            cardinality card.
        """
        estimated_cardinality = (((card/n) - self.prob2 + (self.prob1 * self.prob2)) / self.prob1)*n
        if estimated_cardinality < 0:
            estimated_cardinality = 0
        return int(estimated_cardinality)

    def dp(self, element, uniques):
        """Randomized Response Technique: either report true or a forced value.
        
        Parameters
        ----------
        element: 
            True value/ Current value.
        uniques: list
            Possible values. 
        
        Returns
        -------
            One possbile value. 
        """
        if element not in uniques:
            raise AttributeError('Element is not in uniques')

        if random.random() < self.prob1:
            return element
        else:
            return random.choice(uniques)


class GRR:
    """     
    General Randomized Response. With probability prob1 the true value is
    reported, with probability prob2 one of the other values (opposite of the 
    true value) is reported.

    Attributes
    ----------
    epsilon : double
        differential privacy guarantee. According to epsilon, prob1 and prob2
        are computed.
    dimension : int
        number of discrete quantitative categories
    prob1 : double
        probability to report true value.
    prob2: double
        probability to report one of the other values (opposite of the true value)

    Methods
    -------
    get_probabilities()
        returns prob1 and prob2
    get_cardinality(card, n)
        returns the estimated cardinality
    rrt(element, uniques)
        returns the reported value (true or opposite).
        
    Reference
    ---------
        S. L. Warner. Randomised response: a survey technique for eliminating
        evasive answer bias.Journal of the American Statistical Association,
        60(309):63–69, Mar.1965.
    """
    def __init__(self, epsilon, dimension):
        """
        Parameters
        ----------
        epsilon : double
            differential privacy guarantee. According to epsilon, prob1 and prob2 
            are computed.
        dimension : int
            number of discrete quantitative categories (has to bigger than 1).

        Raises
        ------
        AttributeError
            if epsilon < 0 or dimension <= 1
        """
        if epsilon < 0:
            raise AttributeError('epsilon has to be positive')

        if dimension <= 1:
            raise AttributeError('dimension has to be bigger than 1')

        if epsilon == 0:
            print('WARN: Epsilon == 0: Results will be completely random')

        self.epsilon = epsilon
        self.dimension = dimension
        self.prob1 = math.exp(epsilon) / (math.exp(epsilon) + self.dimension-1)
        self.prob2 = (1-self.prob1)/(self.dimension-1)

    def get_probabilities(self):
        """"
        Returns
        -------
        prob1: double
            probability to report true value.
        prob2: double
            probability to report a forced (one of the possible) value.
        """
        return self.prob1, self.prob2
        
    def get_cardinality(self, card, n):
        """ Unbiased cardinality 
        Parameters
        ----------
        card: int
            Biased number of unique elements for one category.
        n: int
            Total number of elements (sum of cardinality of all categories). 
        
        Returns
        -------
        cardinality : int
            The unbiased cardinality. Corrected with probabilities and biased
            cardinality card.
        """
        estimated_cardinality = (card-(n*self.prob2)) / (self.prob1-self.prob2)
        if estimated_cardinality < 0:
            estimated_cardinality = 0
        return int(estimated_cardinality)
    
    def dp(self, element, uniques):
        """Randomized Response Technique: either report true or a forced value.

        Parameters
        ----------
        element:
            True value/ Current value.
        uniques: list
            Possible values.

        Returns
        -------
            One possbile value.

        Note
        ----
        Forced answer can't be 'element'.
        """
        if element not in uniques:
            raise AttributeError("Element is not in uniques")

        if random.random() < self.prob1:
            return element
        else:
            unique = copy.deepcopy(uniques)
            unique.remove(element)
            return random.choice(uniques)
