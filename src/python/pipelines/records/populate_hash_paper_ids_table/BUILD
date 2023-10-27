python_sources()

pex_binary(
    name="populate_hash_paper_ids_table_main",
    entry_point="main.py",
    dependencies=[
        "//3rdparty/python#pip",
        "//3rdparty/python#setuptools",
    ]
)

python_distribution(
    name="populate_hash_paper_ids_table_dist",
    dependencies=[
        ":populate_hash_paper_ids_table",
        "//3rdparty/python#pip",
    ],
    provides=python_artifact(
        name="populate_hash_paper_ids_table_dist",
        version="1.0",
    ),
)

docker_image(
    name="populate_hash_paper_ids_table_runner",
    dependencies=[
        ":populate_hash_paper_ids_table",
        ":populate_hash_paper_ids_table_dist",
        "//src/protos:protos_dist",
        "//src/python/common:common_dist",
    ],
)
