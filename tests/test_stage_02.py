# Tests originales del proyecto semantic-notes-search de AI Engineering
# from Scratch (https://github.com/rohitg00/ai-engineering-from-scratch,
# MIT License, (c) 2026 Rohit Ghumare). Copiados aqui para que el repo
# sea autocontenido y los tests se puedan correr con:
#   python -m unittest discover tests -v

import json, math, tempfile, unittest
from pathlib import Path
from main import *


class Index(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(build_index({})["idf"], {})

    def test_normalized(self):
        self.assertAlmostEqual(
            sum((v * v for v in build_index({"x": "a a b"})["vectors"]["x"].values())),
            1,
        )

    def test_rare(self):
        self.assertGreater(build_index({"x": "a b", "y": "a"})["idf"]["b"], 1)

    def test_empty_doc(self):
        self.assertEqual(build_index({"x": ""})["vectors"]["x"], {})

    def test_bad_id(self):
        with self.assertRaises(ValueError):
            build_index({"": "a"})

    def test_alias_indexed(self):
        self.assertIn(
            "deploy", build_index({"x": "release"}, {"release": "deploy"})["idf"]
        )
