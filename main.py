import wn
from itertools import combinations
from typing import Set

wn.download("oewn:2024")

print("Building vocabulary...")
base_lemmas: Set[str] = {w.lemma().lower() for w in wn.words()}


def get_lemmas(word: str) -> Set[str]:
    """Strips regular suffixes to find base dictionary lemmas.

    Normalizes a word to lowercase and checks whether it or any of its
    stemmed forms (produced by stripping common English suffixes) exist in
    the WordNet vocabulary.

    Args:
        word: The word to look up, in any case.

    Returns:
        A set of base lemma strings found in the WordNet vocabulary that
        correspond to the input word or its stemmed variants. Empty if no
        match is found.
    """
    lemmas = set()
    word = word.lower()

    if word in base_lemmas:
        lemmas.add(word)

    suffixes = [
        ("ed", ""),  # bombarded -> bombard
        ("ed", "e"),  # baked -> bake
        ("ing", ""),  # jumping -> jump
        ("ing", "e"),  # baking -> bake
        ("s", ""),  # cars -> car
        ("es", ""),  # boxes -> box
    ]

    for suffix, replacement in suffixes:
        if word.endswith(suffix):
            stem = word[: -len(suffix)] + replacement
            if stem in base_lemmas:
                lemmas.add(stem)

    return lemmas


def is_valid_word(word: str) -> bool:
    """Checks if a word resolves to at least one base dictionary lemma.

    Args:
        word: The word to validate.

    Returns:
        True if the word or a stemmed variant exists in the WordNet
        vocabulary, False otherwise.
    """
    return len(get_lemmas(word)) > 0


def is_scattered(parent: str, joey: str) -> bool:
    """Checks whether a joey is a scattered (non-contiguous) subsequence of the parent.

    A joey is considered scattered if it cannot be found as a contiguous
    substring within the parent word. This ensures that valid joeys are
    true subsequences rather than simple substrings.

    Args:
        parent: The parent word to search within.
        joey: The candidate subsequence to test.

    Returns:
        True if ``joey`` does not appear as a contiguous substring of
        ``parent``, False otherwise.
    """
    return joey not in parent


def get_subsequences(word: str, min_length: int = 3) -> Set[str]:
    """Generates valid dictionary subsequences from a word.

    A subsequence is formed by deleting zero or more characters without
    changing the order of the remaining characters. Only subsequences that
    exist in the WordNet lexicon, are not identical to the input word, and
    are not contiguous substrings of the input (i.e. are scattered) are
    returned.

    Args:
        word: The source word from which subsequences are derived.
        min_length: Minimum character length of subsequences to consider.
            Defaults to 3.

    Returns:
        A set of valid scattered subsequences of ``word``.
    """
    word = word.lower()
    found: Set[str] = set()

    for length in range(min_length, len(word)):
        for indices in combinations(range(len(word)), length):
            candidate = "".join(word[i] for i in indices)

            if is_valid_word(candidate) and is_scattered(word, candidate):
                found.add(candidate)

    return found


def get_synset_cluster(lemmas: Set[str]) -> Set[str]:
    """Retrieves an expanded semantic cluster of synsets for a set of lemmas.

    The cluster includes all synsets directly associated with each lemma,
    plus any synsets reachable via ``similar``, ``hypernym``, or ``hyponym``
    relations. This approximates both synonymy and broader/narrower semantic
    relatedness within OEWN.

    Args:
        lemmas: The set of base lemma strings to expand into a synset cluster.

    Returns:
        A set of synset ID strings representing the full semantic cluster.
    """
    cluster: Set[str] = set()
    relations_to_check = ["similar", "hypernym", "hyponym"]

    for lemma in lemmas:
        for w in wn.words(form=lemma):
            for s in w.synsets():
                cluster.add(s.id)
                for rel in relations_to_check:
                    for related in s.get_related(rel):
                        cluster.add(related.id)

    return cluster


def find_kangaroo_words(parent_word: str) -> list[str]:
    """Finds kangaroo words (joeys) contained within a parent word.

    A kangaroo word contains one or more scattered subsequences (joeys) that
    are both valid dictionary words and semantically related to the parent.
    Semantic relatedness is determined by overlap in synset clusters, expanded
    to include hypernym and hyponym relations in addition to direct synonymy.

    Args:
        parent_word: The word to analyze for embedded joey candidates.

    Returns:
        A list of valid joey strings sorted by length, longest first.
    """
    parent_lemmas = get_lemmas(parent_word)
    parent_cluster = get_synset_cluster(parent_lemmas)

    candidates = get_subsequences(parent_word)
    valid_joeys = []

    for c in candidates:
        joey_lemmas = get_lemmas(c)

        if not parent_lemmas.isdisjoint(joey_lemmas):
            continue

        joey_cluster = get_synset_cluster(joey_lemmas)

        if parent_cluster & joey_cluster:
            valid_joeys.append(c)

    return sorted(valid_joeys, key=len, reverse=True)
