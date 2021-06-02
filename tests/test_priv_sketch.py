import unittest
from DP_PDS import priv_sketch
from DP_PDS.dp import rrt
from DP_PDS.sketches import pcsa


class TestPrivSketch(unittest.TestCase):

    def test_init_priv_sketch(self):

        try:
            sketch_dict = {'nmap': 32, 'length': 32}
            priv_sketch.PrivSketch(-1, [1, 2, 3], rrt.GRR, pcsa.PCSA, sketch_dict)
            self.fail('exception expected')
        except AttributeError as inst:
            self.assertEqual('epsilon has to be positive', str(inst))

        try:
            sketch_dict = {'nmap': 32, 'length': 32}
            priv_sketch.PrivSketch(300, [], rrt.GRR, pcsa.PCSA, sketch_dict)
            self.fail('exception expected')
        except AttributeError as inst:
            self.assertEqual('size of uniques has to be bigger than 0', str(inst))

        try:
            sketch_dict = {'nmap': 32, 'length': 32}
            priv_sketch.PrivSketch(300, [], rrt.GRR, pcsa.PCSA, sketch_dict, hash_function=priv_sketch)
            self.fail('exception expected')
        except AttributeError as inst:
            self.assertEqual('hash function class needs to have an .hash(key) method', str(inst))

        try:
            sketch_dict = {'nmap': 32, 'length': 32}
            priv_sketch.PrivSketch(300, [1, 2, 3], rrt.GRR, pcsa.PCSA, sketch_dict)
        except Exception as inst:
            self.fail('unexpected exception')

    def test_union(self):
        sketch_dict = {'nmap': 32, 'length': 32}
        ps = priv_sketch.PrivSketch(300, [1, 2, 3], rrt.GRR, pcsa.PCSA, sketch_dict)

        pcsa1 = pcsa.PCSA(1, 3)
        pcsa1.bitmap[0][0] = True
        pcsa2 = pcsa.PCSA(1, 3)
        pcsa2.bitmap[0][1] = True
        pcsa3 = pcsa.PCSA(1, 3)
        pcsa3.bitmap[0][2] = True
        ps.sketch = {0: pcsa1, 1: pcsa2, 2: pcsa3}

        union = ps.union(ps.sketch)
        exp = pcsa.PCSA(1, 3)
        exp.bitmap[0][0] = True
        exp.bitmap[0][1] = True
        exp.bitmap[0][2] = True
        self.assertListEqual(exp.bitmap, union.bitmap)

    def test_count_dp(self):
        sketch_dict = {'nmap': 32, 'length': 32}
        ps = priv_sketch.PrivSketch(300, [1, 2, 3], rrt.GRR, pcsa.PCSA, sketch_dict)

        try:
            ps.count_dp('1', 1)
        except Exception as inst:
            self.fail('unexpected exception')

    def test_get_estimated_cardinality(self):
        sketch_dict = {'nmap': 32, 'length': 32}
        ps = priv_sketch.PrivSketch(300, [1, 2, 3], rrt.GRR, pcsa.PCSA, sketch_dict)

        try:
            ps.count_dp('1', 1)
            ps.get_estimated_cardinality(1)
        except Exception as inst:
            self.fail('unexpected exception')


if __name__ == '__main__':
    unittest.main()
