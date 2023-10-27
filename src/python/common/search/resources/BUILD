files(
    name="dictionaries",
    sources=["*.txt"],
)

relocated_files(
    name="relocated_dictionaries",
    files_targets=[":dictionaries"],
    src="src/python/common/search/resources",
    dest="dictionaries"
)

archive(
    name="search_resources",
    format="zip",
    files=[":relocated_dictionaries"],
)