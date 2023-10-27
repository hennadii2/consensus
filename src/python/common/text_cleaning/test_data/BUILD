files(sources=["raw_semantic_scholar_s2-corpus-000_2022-01-01/*"])

python_sources(
  name="python_sources",
)

pex_binary(
    name="update_test_data",
    entry_point="update_test_data.py",
    dependencies=[
        ":python_sources",
        "//src/python/common/text_cleaning/test_data:test_data",
    ],
)

pex_binary(
    name="generate_test_data",
    entry_point="generate_test_data.py",
    dependencies=[
        ":python_sources",
        "//src/mock_data:mock_data",
        "//src/python/common/text_cleaning/test_data:test_data",
    ],
)
