from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

# Trie for Keyword Matching
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

    def search(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        return self._collect_words(node, prefix)

    def _collect_words(self, node, prefix):
        words = []
        if node.is_end_of_word:
            words.append(prefix)
        for char, child in node.children.items():
            words.extend(self._collect_words(child, prefix + char))
        return words

# N-ary Tree for Content Hierarchy
class Node:
    def __init__(self, tag, content=None):
        self.tag = tag
        self.content = content
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

# Red-Black Tree for Efficient Search & Ranking
class RBTreeNode:
    def __init__(self, tag, relevance, color="red"):
        self.tag = tag
        self.relevance = relevance
        self.color = color
        self.left = None
        self.right = None

class RBTree:
    def __init__(self):
        self.root = None

    def insert(self, tag, relevance):
        new_node = RBTreeNode(tag, relevance)
        if not self.root:
            new_node.color = "black"  # root is always black
            self.root = new_node
        else:
            self.root = self._insert_recursive(self.root, new_node)

    def _insert_recursive(self, current, node):
        if not current:
            return node

        if node.relevance < current.relevance:
            current.left = self._insert_recursive(current.left, node)
        elif node.relevance > current.relevance:
            current.right = self._insert_recursive(current.right, node)

        # Red-black balancing would go here (simplified for demonstration)
        return current

    def in_order_traversal(self, node):
        if node:
            yield from self.in_order_traversal(node.left)
            yield node.tag, node.relevance
            yield from self.in_order_traversal(node.right)

# Hybrid System: Combines Trie, N-ary Tree, and Red-Black Tree
class HybridSEOSystem:
    def __init__(self):
        self.trie = Trie()
        self.hierarchy = Node("SEO Elements")
        self.rank_tree = RBTree()
        self.analysis_results = []

    def reset(self):
        self.hierarchy = Node("SEO Elements")  # Reset the hierarchy
        self.rank_tree = RBTree()  # Reset the ranking tree

    def search_webpages(self, keywords):
        self.reset()  # Reset previous results
        search_url = f"https://www.google.com/search?q={'+'.join(keywords.split())}"
        try:
            response = requests.get(search_url)
            soup = BeautifulSoup(response.content, 'html.parser')

            results = []
            for item in soup.find_all('h3'):  # Example for Google search results
                title = item.text
                link = item.find_parent('a')['href']

                # Ensure link is a valid URL and not a redirect
                if link.startswith('/url?q='):
                    link = link.split('/url?q=')[1].split('&')[0]  # Extract the actual URL
                    meta_description = self.fetch_meta_description(link)
                    self.fetch_and_analyze(link)  # Analyze the fetched URL
                    results.append((title, link, meta_description))

            return results
        except requests.exceptions.RequestException as e:
            print(f"Error fetching search results: {e}")
            return []

    def fetch_meta_description(self, url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            meta = soup.find('meta', attrs={'name': 'description'})
            return meta['content'] if meta else "No meta description found"
        except:
            return "Error fetching meta description."

    def fetch_and_analyze(self, url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Title Tag
            title_tag = soup.find('title')
            title_content = title_tag.text if title_tag else "No title tag found"
            title_node = Node("Title", title_content)
            self.hierarchy.add_child(title_node)
            self.trie.insert("title")
            self.rank_tree.insert("Title", relevance=10)

            # Meta Description
            meta_description = soup.find('meta', attrs={'name': 'description'})
            desc_content = meta_description['content'] if meta_description else "No meta description found"
            desc_node = Node("Meta Description", desc_content)
            self.hierarchy.add_child(desc_node)
            self.trie.insert("meta description")
            self.rank_tree.insert("Meta Description", relevance=8)

            # Open Graph Tags
            og_title = soup.find('meta', property='og:title')
            og_title_content = og_title['content'] if og_title else "No Open Graph title found"
            og_node = Node("Open Graph Title", og_title_content)
            self.hierarchy.add_child(og_node)
            self.trie.insert("og title")
            self.rank_tree.insert("OG Title", relevance=6)

            # Store results
            self.analysis_results.append({
                "url": url,
                "title": title_content,
                "meta_description": desc_content,
                "og_title": og_title_content
            })
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")

    def search_keywords(self, prefix):
        return self.trie.search(prefix)

    def print_hierarchy(self, node, level=0):
        print(" " * level * 2 + f"{node.tag}: {node.content if node.content else ''}")
        for child in node.children:
            self.print_hierarchy(child, level + 1)

    def print_ranked_results(self):
        print("Ranked SEO elements:")
        for tag, relevance in self.rank_tree.in_order_traversal(self.rank_tree.root):
            print(f"{tag}: relevance {relevance}")

    def print_analysis_results(self):
        for result in self.analysis_results:
            print(f"\nURL: {result['url']}")
            print(f"Title: {result['title']}")
            print(f"Meta Description: {result['meta_description']}")
            print(f"Open Graph Title: {result['og_title']}")

app = Flask(__name__)
hybrid_seo = HybridSEOSystem()

@app.route('/')
def home():
    return render_template('index.html')  # This renders your HTML page

@app.route('/search', methods=['POST'])
def search():
    keywords = request.form['keywords']  # Get the keywords from the form
    results = hybrid_seo.search_webpages(keywords)  # Fetch results based on keywords
    formatted_results = [
        {
            "title": title,
            "link": link,
            "description": description
        }
        for title, link, description in results
    ]
    return jsonify(formatted_results)  # Return results as JSON

if __name__ == '__main__':
    app.run(debug=True)
