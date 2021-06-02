import unittest
from DP_PDS.sketches import pcsa
from bitarray import bitarray
import mmh3


class TestPCSA(unittest.TestCase):

    def test_init(self):
        try:
            pcsa.PCSA(0, 32)
            self.fail('exception expected')
        except AttributeError as inst:
            self.assertEqual('nmap and length have to be at least 1', str(inst))

        try:
            pcsa.PCSA(32, -1)
            self.fail('exception expected')
        except AttributeError as inst:
            self.assertEqual('nmap and length have to be at least 1', str(inst))

        try:
            pcsa.PCSA(32, 32, pcsa)
            self.fail('exception expected')
        except AttributeError as inst:
            self.assertEqual('hash function class needs to have an .hash(key) method', str(inst))

        try:
            pcsa_obj = pcsa.PCSA(32, 32, mmh3)
            bitmap = [bitarray(32) for i in range(32)]
            for array in bitmap:
                array.setall(0)
            self.assertListEqual(bitmap, pcsa_obj.sketch())
        except Exception:
            self.fail('unexpected exception')

    def test_sizeof(self):
        pcsa_obj = pcsa.PCSA(32, 32)
        self.assertEqual(32*32/8, pcsa_obj.sizeof())

    def test_add(self):
        pcsa_obj = pcsa.PCSA(32, 32)
        contains = 0
        for array in pcsa_obj.sketch():
            if array.any():
                contains += 1
        self.assertEqual(0, contains)

        pcsa_obj.add('test')

        contains = 0
        for array in pcsa_obj.sketch():
            if array.any():
                contains += 1
        self.assertEqual(1, contains)

    def test_count(self):
        pcsa_obj = pcsa.PCSA(32, 32)
        count1 = pcsa_obj.count()
        self.assertEqual(0, count1)

        pcsa_obj.add('test')

        count2 = pcsa_obj.count()
        self.assertNotEqual(count1, count2)

    def test_calculate_prop_factor(self):
        pcsa_obj = pcsa.PCSA(32, 32)
        self.assertEqual(0.773519, pcsa_obj.PHI)

        pcsa_obj.calculate_prop_factor(1.0)
        self.assertEqual(1e-05, pcsa_obj.PHI)

        pcsa_obj.calculate_prop_factor(0.5)
        self.assertEqual(1.8483246464054996, pcsa_obj.PHI)

    def test_union(self):
        pcsas = [pcsa.PCSA(32, 32), pcsa.PCSA(64, 32)]
        try:
            pcsa.PCSA.union(pcsas)
            self.fail('exception expected')
        except AttributeError as inst:
            self.assertEqual('sketches have different values for nmap', str(inst))

        pcsas = [pcsa.PCSA(32, 32), pcsa.PCSA(32, 64)]
        try:
            pcsa.PCSA.union(pcsas)
            self.fail('exception expected')
        except AttributeError as inst:
            self.assertEqual('sketches have different values for length', str(inst))

        pcsas = [pcsa.PCSA(32, 32), pcsa.PCSA(32, 32, DummyHash)]
        try:
            pcsa.PCSA.union(pcsas)
            self.fail('exception expected')
        except AttributeError as inst:
            self.assertEqual('pcsa objects use different hash functions', str(inst))

        pcsa1 = pcsa.PCSA(1, 3)
        pcsa1.bitmap[0][0] = True
        pcsa2 = pcsa.PCSA(1, 3)
        pcsa2.bitmap[0][2] = True
        union = pcsa.PCSA.union([pcsa1, pcsa2])

        exp = pcsa.PCSA(1, 3)
        exp.bitmap[0][0] = True
        exp.bitmap[0][2] = True

        self.assertListEqual(exp.bitmap, union.bitmap)


class DummyHash:
    def hash(self):
        return 1


if __name__ == '__main__':
    unittest.main()
