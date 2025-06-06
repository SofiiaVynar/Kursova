from graphviz import Digraph
import os

dot_path = r"C:\Program Files\Graphviz\bin"
os.environ["PATH"] += os.pathsep + dot_path


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word

    def starts_with(self, prefix):
        node = self.root
        words = []

        for char in prefix:
            if char not in node.children:
                return False, []
            node = node.children[char]

        self.with_prefix(node, prefix, words)
        return True, words

    def with_prefix(self, node, prefix, words):
        if node.is_end_of_word:
            words.append(prefix)

        for char, child_node in node.children.items():
            self.with_prefix(child_node, prefix + char, words)

    def visualize(self):
        dot = Digraph()

        def add_nodes(current_node, prefix):
            for char, child_node in current_node.children.items():
                new_prefix = prefix + char
                dot.node(new_prefix, label=char, shape='circle')
                dot.edge(prefix, new_prefix)
                add_nodes(child_node, new_prefix)
        add_nodes(self.root, '')
        dot.render('trie_visualization', format='jpg', view=True)


def build_trie(patterns):
    trie = Trie()
    for pattern in patterns:
        trie.insert(pattern)
    return trie


patterns = ["abandon", "ability", "able", "abortion", "about", "above", "abroad", "absence", "absolute", "absolutely",
            "absorb", "abuse", "academic", "accept", "access", "accident", "accompany", "accomplish", "according",
            "account", "accurate", "accuse", "achieve", "achievement"]
trie_obj = build_trie(patterns)

print(trie_obj.search("app"))
print(trie_obj.search("able"))
print(trie_obj.search("ban"))
print(trie_obj.search("ca"))
print(trie_obj.search("about"))
print("\n")

found, words = trie_obj.starts_with("acc")
print(found)
print(words)

found, words = trie_obj.starts_with("be")
print(found)
print(words)

found, words = trie_obj.starts_with("ad")
print(found)
print(words)

found, words = trie_obj.starts_with("c")
print(found)
print(words)

trie_obj.visualize()
