#!/usr/bin/env python3
"""Verificacao local da expressao g observada no AVM2 do SWF original.

Este teste executa Python, NAO ActionScript nem o cliente Flash.
Os blocos AVM2 correspondentes foram estudados no lote 3G.
"""
import math
import unittest

def literal_cost(current_g, diagonal):
    test = current_g + int(diagonal)
    truthy = not (test == 0 or math.isnan(test))
    return 14 if truthy else 10

def conventional_cost(current_g, diagonal):
    return current_g + (14 if diagonal else 10)

class AStarCostTest(unittest.TestCase):
    def test_literal_values(self):
        cases=[
            (float("nan"),False,10),
            (float("nan"),True,10),
            (0,False,10),
            (0,True,14),
            (10,False,14),
            (10,True,14),
            (14,False,14),
        ]
        for cost, diagonal, expected in cases:
            with self.subTest(g=cost,diag=diagonal):
                self.assertEqual(literal_cost(cost,diagonal),expected)

    def test_not_the_same_as_conventional_cost(self):
        self.assertEqual(literal_cost(10,False),14)
        self.assertEqual(conventional_cost(10,False),20)

    def test_existing_candidate_branch(self):
        # O original altera o pai somente quando novo g < g antigo.
        original_g=25
        g=literal_cost(0,True)
        should_update=(g < original_g)
        self.assertTrue(should_update)
        self.assertEqual(g,14)

if __name__=="__main__":
    unittest.main(verbosity=2)
