import wn
from itertools import combinations
from typing import Set

wn.download("oewn:2024")

all_words: Set[str] = {w.lemma() for w in wn.words()}


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
            if candidate in all_words and candidate != word:
                found.add(candidate)

    return found


def get_synset_cluster(word: str) -> Set[str]:
    """Retrieve a semantic cluster of synsets for a word.

    The cluster includes:
        - All synsets directly associated with the word.
        - Any synsets reachable via a single 'similar' relation,
        which approximates synonymy in OEWN.

    Args:
        word (str): The target word.

    Returns:
        set[str]: A set of synset IDs representing the semantic cluster.
    """
    cluster: Set[str] = set()

    for s in wn.synsets(word):
        cluster.add(s.id)
        for related in s.get_related("similar"):
            cluster.add(related.id)

    return cluster


def find_kangaroo_words(parent_word: str) -> list[str]:
    """Find kangaroo words for a given parent word.

    A kangaroo word contains one or more subsequences (joeys) that are:
        - Valid dictionary words.
        - Semantically related to the parent word.

    Semantic relatedness is approximated via overlap in synset clusters.

    Args:
        parent_word (str): The word to analyze.

    Returns:
        list[str]: A list of kangaroo candidates sorted by length
        (longest first).
    """
    candidates: Set[str] = get_subsequences(parent_word)
    parent_cluster: Set[str] = get_synset_cluster(parent_word)

    return sorted(
        [c for c in candidates if parent_cluster & get_synset_cluster(c)],
        key=len,
        reverse=True,
    )
