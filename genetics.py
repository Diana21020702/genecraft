"""Educational, independent-assortment Mendelian genetics engine."""
from __future__ import annotations
from collections import Counter
from fractions import Fraction
from itertools import product


def parse_genotype(text: str) -> tuple[str, ...]:
    """Accept e.g. 'Aa' or 'Aa Bb'; return canonical two-character loci."""
    if not isinstance(text, str):
        raise ValueError("Genotyp musí být text.")
    loci = text.strip().split()
    if not 1 <= len(loci) <= 2:
        raise ValueError("Zadej jeden nebo dva geny, například Aa nebo Aa Bb.")
    used = set()
    normalized = []
    for locus in loci:
        if len(locus) != 2 or not locus.isascii() or not locus.isalpha():
            raise ValueError("Každý gen musí mít dvě písmena, např. Aa, BB nebo cc.")
        letter = locus[0].upper()
        if letter == locus[0].lower() or locus[1].upper() != letter:
            raise ValueError("V jednom genu musí být stejné písmeno, např. Aa.")
        if letter in used:
            raise ValueError("Každý gen se může vyskytovat jen jednou.")
        used.add(letter)
        normalized.append("".join(sorted(locus, key=lambda c: c.islower())))
    return tuple(sorted(normalized, key=lambda x: x[0].upper()))


def gametes(loci: tuple[str, ...]) -> list[str]:
    """Return each distinct gamete with correct multiplicity."""
    return ["".join(items) for items in product(*[tuple(locus) for locus in loci])]


def make_cross(parent1: str, parent2: str) -> dict:
    first, second = parse_genotype(parent1), parse_genotype(parent2)
    if [x[0].upper() for x in first] != [x[0].upper() for x in second]:
        raise ValueError("Oba rodiče musí mít stejné geny ve stejných lokusech.")
    g1, g2 = gametes(first), gametes(second)
    count = Counter()
    phenotypes = Counter()
    table = []
    for a in g1:
        row = []
        for b in g2:
            pairs = ["".join(sorted(x + y, key=lambda c: c.islower())) for x, y in zip(a, b)]
            genotype = " ".join(pairs)
            phenotype = " ".join(
                f"{pair[0].upper()}: dominantní" if any(c.isupper() for c in pair)
                else f"{pair[0].upper()}: recesivní" for pair in pairs
            )
            row.append(genotype)
            count[genotype] += 1
            phenotypes[phenotype] += 1
        table.append(row)
    total = len(g1) * len(g2)
    def probabilities(counter: Counter) -> list[dict]:
        return [
            {"label": key, "count": val, "fraction": str(Fraction(val, total)),
             "percent": round(val / total * 100, 2)}
            for key, val in sorted(counter.items(), key=lambda x: (-x[1], x[0]))
        ]
    return {
        "parents": [" ".join(first), " ".join(second)],
        "gametes": [g1, g2], "table": table, "total": total,
        "genotypes": probabilities(count), "phenotypes": probabilities(phenotypes),
        "note": "Model předpokládá úplnou dominanci a nezávislou kombinovatelnost genů."
    }
