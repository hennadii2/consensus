"""
Standalone script for estimating average time for metadata sorting.
"""

import random
import time
from argparse import ArgumentParser
from dataclasses import dataclass
from functools import cmp_to_key

from loguru import logger


@dataclass(frozen=True)
class Claim:
    prob: float
    cite: int
    year: int
    similarity: float
    text: str


@dataclass(frozen=True)
class NormalizationParams:
    similarity_weight: float
    prob_weight: float
    cite_weight: float
    year_weight: float
    min_year: int
    max_year: int
    min_cite: int
    max_cite: int


NORMALIZATION_PARAMS = NormalizationParams(
    similarity_weight=1.0,
    prob_weight=0.5,
    cite_weight=0.15,
    year_weight=0.05,
    min_year=1970,
    max_year=2022,
    min_cite=0,
    max_cite=10,
)


def calculate_sorting_score(claim: Claim, params: NormalizationParams) -> float:
    prob_score = (claim.prob - 0.5) / (1.0 - 0.5)

    cite_score = (claim.cite - params.min_cite) / (params.max_cite - params.min_cite)
    cite_score = max(0.0, min(1.0, cite_score))

    year_score = (claim.year - params.min_year) / (params.max_year - params.min_year)
    year_score = max(0.0, min(1.0, year_score))

    return (
        prob_score * params.prob_weight
        + cite_score * params.cite_weight
        + year_score * params.year_weight
        + claim.similarity * params.similarity_weight
    )


def sort_by_metadata(a: Claim, b: Claim) -> int:
    a_score = calculate_sorting_score(a, NORMALIZATION_PARAMS)
    b_score = calculate_sorting_score(b, NORMALIZATION_PARAMS)
    if a_score < b_score:
        return -1
    elif a_score > b_score:
        return 1
    else:
        return 0


def generate_claims(count: int) -> list[Claim]:
    claims = []
    for i in range(count):
        claims.append(
            Claim(
                text=f"sentence:{i}",
                prob=random.random(),
                cite=random.randint(0, 250),
                year=random.randint(1900, 2023),
                similarity=random.random(),
            )
        )
    return claims


def main(argv=None):
    parser = ArgumentParser()
    parser.add_argument("--count", dest="count", type=int, required=True)
    args = parser.parse_args()

    claims = generate_claims(count=args.count)

    num_trials = 10
    timing_ns = []
    for i in range(num_trials):
        start_ns = time.perf_counter_ns()

        sorted(claims, key=cmp_to_key(sort_by_metadata), reverse=True)

        end_ns = time.perf_counter_ns()
        timing_ns.append(end_ns - start_ns)

    avg_timing_seconds = (sum(timing_ns) / num_trials) / 10**9
    logger.info(f"Average sort timing: {avg_timing_seconds} seconds")


if __name__ == "__main__":
    main()
