import glob
import re
from pathlib import Path

from common.text_cleaning.base_text_cleaner import BaseTextCleaner

TEST_DATA_BASE_PATH = "src/python/common/text_cleaning/test_data"
TEST_DATA_PATTERNS = [
    "raw_semantic_scholar_s2-corpus-000_2022-01-01/*_raw",
]


def test_clean_text_on_all_test_data_succeeds() -> None:
    test_data_pairs = []
    for pattern in TEST_DATA_PATTERNS:
        pattern_path = f"{TEST_DATA_BASE_PATH}/{pattern}"
        raw_files = glob.glob(pattern_path)
        for raw_file in raw_files:
            cleaned_file = re.sub(r"_raw$", "_cleaned", raw_file)
            test_data_pairs.append((raw_file, cleaned_file))

    assert len(test_data_pairs) > 0

    base_text_cleaner = BaseTextCleaner()
    for test_data in test_data_pairs:
        raw_path, expected_path = test_data
        actual = base_text_cleaner.clean_text(Path(raw_path).read_text())
        expected = Path(expected_path).read_text()
        assert actual == expected


def test_clean_text_succeeds() -> None:
    base_text_cleaner = BaseTextCleaner()

    test = r"""
    [[[    we study             ]]]    {{{the structure of th}}}e  . ((( mather and aubry sets))) for the family of lagrangians given
    by the kinetic energy associated to a riemannian metric $ g$ on a closed manifold $ m$.
    in this case the (  euler-lagrange  ) flow is the {    geodesic  } flow of $(m,g)$. we prove that there exists a
    50% residual subset $ \mathcal g$ of the set of all conformal metrics to $g$, such that,
    if $ \overline g \in \mathcal g$ then the corresponding geodesic flow has a
    finitely many ergodic c-minimizing measures, for each non-trivial cohomology
    class $ c \in h^1(m,\mathbb{r})$. this implies that, for any$ c \in h^1(m,\mathbb{r})$ ,
    the quotient aubry set for the cohomology class c has a finite number of elements for
    this particular family of lagrangian systems.???!!!!
    `aa` % Dr.Strangelove  12,000 ali,megan   Mrs....         aaaa $ 2฿
    """  # noqa: E501

    actual = base_text_cleaner.clean_text(test)
    expected = r"[we study] the structure of the. (mather and aubry sets) for the family of lagrangians given by the kinetic energy associated to a riemannian metric g on a closed manifold m. in this case the (euler-lagrange) flow is the geodesic flow of (m,g). we prove that there exists a 50% residual subset ℊ of the set of all conformal metrics to g, such that, if g∈ℊ then the corresponding geodesic flow has a finitely many ergodic c-minimizing measures, for each non-trivial cohomology class c ∈ h^1(m,𝕣). this implies that, for anyc ∈ h^1(m,𝕣) , the quotient aubry set for the cohomology class c has a finite number of elements for this particular family of lagrangian systems.?! 'aa' % DrStrangelove 12,000 ali, megan Mrs aaaa 2THB"  # noqa: E501
    assert actual == expected
