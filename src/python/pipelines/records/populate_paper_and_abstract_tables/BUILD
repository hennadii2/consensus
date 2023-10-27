python_sources()

pex_binary(
    name="populate_paper_and_abstract_tables_main",
    entry_point="main.py",
    dependencies=[
        "//3rdparty/python#pip",
    ]
)

python_distribution(
    name="populate_paper_and_abstract_tables_dist",
    dependencies=[
        ":populate_paper_and_abstract_tables",
        "//3rdparty/python#pip",
    ],
    provides=python_artifact(
        name="populate_paper_and_abstract_tables_dist",
        version="1.0",
    ),
)

docker_image(
    name="populate_paper_and_abstract_tables_runner",
    dependencies=[
        ":populate_paper_and_abstract_tables",
        ":populate_paper_and_abstract_tables_dist",
        "//src/protos:protos_dist",
        "//src/python/common:common_dist",
    ],
)
