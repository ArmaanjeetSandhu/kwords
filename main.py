import wn
from itertools import combinations
from typing import Set

wn.download("oewn:2024")

print("Building vocabulary...")
all_valid_forms: Set[str] = set()
for w in wn.words():
    all_valid_forms.add(w.lemma().lower())
    for form in w.forms():
        all_valid_forms.add(form.lower())


def get_subsequences(word: str, min_length: int = 3) -> Set[str]:
    """Generate valid dictionary subsequences from a word.

    A subsequence is formed by deleting zero or more characters without
    changing the order of the remaining characters.

    Args:
        word (str): The source word.
        min_length (int, optional): Minimum length of subsequences to consider.
            Defaults to 3.

    Returns:
        set[str]: A set of valid subsequences that:
            - Exist in the WordNet lexicon.
            - Are not identical to the input word.
    """
    word = word.lower()
    found: Set[str] = set()

    for length in range(min_length, len(word)):
        for indices in combinations(range(len(word)), length):
            candidate = "".join(word[i] for i in indices)
            if candidate in all_valid_forms and candidate != word:
                found.add(candidate)

    return found


def get_synset_cluster(word: str) -> Set[str]:
    """Retrieve an expanded semantic cluster of synsets for a word.

    The cluster includes:
        - All synsets directly associated with the word.
        - Any synsets reachable via 'similar', 'hypernym', or 'hyponym'
          relations, approximating both synonymy and broader/narrower
          semantic relatedness in OEWN.

    Args:
        word (str): The target word.

    Returns:
        set[str]: A set of synset IDs representing the semantic cluster.
    """
    cluster: Set[str] = set()
    relations_to_check = ["similar", "hypernym", "hyponym"]

    for w in wn.words(form=word):
        for s in w.synsets():
            cluster.add(s.id)
            for rel in relations_to_check:
                for related in s.get_related(rel):
                    cluster.add(related.id)

    return cluster


def find_kangaroo_words(parent_word: str) -> list[str]:
    """Find kangaroo words for a given parent word.

    A kangaroo word contains one or more subsequences (joeys) that are:
        - Valid dictionary words.
        - Semantically related to the parent word.

    Semantic relatedness is approximated via overlap in synset clusters,
    expanded to include hypernym and hyponym relations in addition to
    synonymy.

    Args:
        parent_word (str): The word to analyze.

    Returns:
        list[str]: A list of kangaroo candidates sorted by length
        (longest first).
    """
    candidates: Set[str] = get_subsequences(parent_word)
    parent_cluster: Set[str] = get_synset_cluster(parent_word)

    valid_joeys = []
    for c in candidates:
        if parent_cluster & get_synset_cluster(c):
            valid_joeys.append(c)

    return sorted(valid_joeys, key=len, reverse=True)
