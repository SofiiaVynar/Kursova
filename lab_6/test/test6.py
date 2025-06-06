import unittest

from src.lab_6 import Trie


class TestTrie(unittest.TestCase):
    def setUp(self):
        self.trie = Trie()
        self.patterns = ["abandon", "ability", "able", "abortion", "about", "above"]
        for pattern in self.patterns:
            self.trie.insert(pattern)

    def test_search_existing_word(self):
        self.assertTrue(self.trie.search("abandon"))
        self.assertTrue(self.trie.search("able"))
        self.assertFalse(self.trie.search("null"))
        self.assertFalse(self.trie.search("cool"))

    def with_prefix(self):
        found, words = self.trie.starts_with("ab")
        self.assertTrue(found)
        self.assertCountEqual(words, ["abandon", "ability", "able", "abortion", "about", "above"])

        found, words = self.trie.starts_with("be")
        self.assertFalse(found)
        self.assertCountEqual(words, [])

        found, words = self.trie.starts_with("aba")
        self.assertTrue(found)
        self.assertCountEqual(words, ["abandon"])

        found, words = self.trie.starts_with("c")
        self.assertTrue(found)
        self.assertCountEqual(words, [])


if __name__ == "__main__":
    unittest.main()
