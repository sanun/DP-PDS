import unittest
from DP_PDS.dp import rrt
import math


class TestRRT(unittest.TestCase):

    def test_init_rrt(self):

        try:
            rrt.RRT(-1, 3)
            self.fail('exception expected')
        except AttributeError as inst:
            self.assertEqual('epsilon has to be positive', str(inst))

        try:
            rrt.RRT(300, 1)
            self.fail('exception expected')
        except AttributeError as inst:
            self.assertEqual('dimension has to be bigger than 1', str(inst))

        try:
            rrt.RRT(300, 3)
        except Exception:
            self.fail('unexpected exception')

    def test_get_probabilities_rrt(self):
        rrt_obj = rrt.RRT(300, 3)
        prob1 = (math.exp(300) - 1) / (math.exp(300) + 2)
        self.assertEqual((prob1, 1/3), rrt_obj.get_probabilities())

    def test_get_cardinality_rrt(self):
        rrt_obj = rrt.RRT(3, 2)
        self.assertEqual(0, rrt_obj.get_cardinality(1, 100))

        rrt_obj = rrt.RRT(300, 3)
        exp = (((10/1000) - rrt_obj.prob2 + (rrt_obj.prob1 * rrt_obj.prob2)) / rrt_obj.prob1)*1000
        self.assertEqual(int(exp), rrt_obj.get_cardinality(10, 1000))

        rrt_obj = rrt.RRT(300, 3)
        exp = (((1000/10) - rrt_obj.prob2 + (rrt_obj.prob1 * rrt_obj.prob2)) / rrt_obj.prob1)*10
        self.assertEqual(int(exp), rrt_obj.get_cardinality(1000, 10))

    def test_dp_rrt(self):
        rrt_obj = rrt.RRT(3, 2)
        try:
            rrt_obj.dp(1, [2, 3])
            self.fail('exception expected')
        except AttributeError as inst:
            self.assertEqual('Element is not in uniques', str(inst))

        array = [1, 2, 3]
        self.assertTrue(rrt_obj.dp(1, array) in array)

    def test_init_grr(self):

        try:
            rrt.GRR(-1, 3)
            self.fail('exception expected')
        except AttributeError as inst:
            self.assertEqual('epsilon has to be positive', str(inst))

        try:
            rrt.GRR(300, 1)
            self.fail('exception expected')
        except AttributeError as inst:
            self.assertEqual('dimension has to be bigger than 1', str(inst))

        try:
            rrt.GRR(300, 3)
        except Exception:
            self.fail("unexpected exception")

    def test_get_probabilities_grr(self):
        rrt_obj = rrt.GRR(300, 3)
        prob1 = math.exp(300) / (math.exp(300) + 2)
        prob2 = (1-prob1)/2
        self.assertEqual((prob1, prob2), rrt_obj.get_probabilities())

    def test_get_cardinality_grr(self):
        rrt_obj = rrt.GRR(3, 3)
        self.assertEqual(0, rrt_obj.get_cardinality(1, 100))

        rrt_obj = rrt.GRR(300, 3)
        exp = (1 - (100 * rrt_obj.prob2)) / (rrt_obj.prob1 - rrt_obj.prob2)
        self.assertEqual(int(exp), rrt_obj.get_cardinality(1, 100))

        rrt_obj = rrt.GRR(300, 3)
        exp = (1000 - (10 * rrt_obj.prob2)) / (rrt_obj.prob1 - rrt_obj.prob2)
        self.assertEqual(int(exp), rrt_obj.get_cardinality(1000, 10))

    def test_dp_grr(self):
        rrt_obj = rrt.GRR(3, 2)
        try:
            rrt_obj.dp(1, [2, 3])
            self.fail('exception expected')
        except AttributeError as inst:
            self.assertEqual('Element is not in uniques', str(inst))

        rrt_obj.dp(1, [1, 2, 3])


if __name__ == '__main__':
    unittest.main()
