import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from app.calculatrice import addition, soustraction, multiplication, division, puissance, modulo, calcul_complexe

class TestCalculatrice(unittest.TestCase):
    def test_addition(self): 
        self.assertEqual(addition(3, 4), 7)
        self.assertEqual(addition(-1, 1), 0)

    def test_soustraction(self):
        self.assertEqual(soustraction(10, 3), 7)
        self.assertEqual(soustraction(0, 5), -5)

    def test_multiplication(self):
        self.assertEqual(multiplication(5, 6), 30)
        self.assertEqual(multiplication(-2, 3), -6)

    def test_division(self):
        self.assertEqual(division(10, 2), 5)
        with self.assertRaises(ValueError):
            division(5, 0)

    def test_puissance(self):
        self.assertEqual(puissance(2, 3), 8)
        self.assertEqual(puissance(5, 0), 1)

    def test_modulo(self):
        self.assertEqual(modulo(10, 3), 1)
        with self.assertRaises(ValueError):
            modulo(10, 0)

    def test_calcul_complexe(self):
        self.assertEqual(calcul_complexe(2, 3), puissance(2, 3) + 10)

if __name__ == "__main__":
    unittest.main()
