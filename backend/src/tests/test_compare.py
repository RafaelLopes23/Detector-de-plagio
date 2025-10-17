import unittest
from plagiarism_detector.compare import compare_texts, detect_plagiarism

class TestCompare(unittest.TestCase):

    def test_identical_texts(self):
        text1 = "This is a sample text."
        text2 = "This is a sample text."
    self.assertAlmostEqual(compare_texts(text1, text2), 1.0)

    def test_different_texts(self):
        text1 = "This is a sample text."
        text2 = "This is a different text."
    self.assertLess(compare_texts(text1, text2), 1.0)

    def test_similar_texts(self):
        text1 = "This is a sample text."
        text2 = "This sample text is a."
    self.assertGreater(compare_texts(text1, text2), 0.5)

    def test_empty_texts(self):
        text1 = ""
        text2 = ""
    self.assertAlmostEqual(compare_texts(text1, text2), 1.0)

    def test_one_empty_text(self):
        text1 = "This is a sample text."
        text2 = ""
    self.assertFalse(detect_plagiarism(text1, text2, threshold=0.2))

if __name__ == '__main__':
    unittest.main()