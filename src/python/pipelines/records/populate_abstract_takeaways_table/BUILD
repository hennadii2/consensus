python_sources()

pex_binary(
    name="populate_abstract_takeaways_table_main",
    entry_point="main.py",
    dependencies=[
        "//3rdparty/python#pip",
        "//3rdparty/python#setuptools",
    ]
)

python_distribution(
    name="populate_abstract_takeaways_table_dist",
    dependencies=[
        ":populate_abstract_takeaways_table",
        "//3rdparty/python#pip",
    ],
    provides=python_artifact(
        name="populate_abstract_takeaways_table_dist",
        version="1.0",
    ),
)

docker_image(
    name="populate_abstract_takeaways_table_runner",
    dependencies=[
        ":populate_abstract_takeaways_table",
        ":populate_abstract_takeaways_table_dist",
        "//src/protos:protos_dist",
        "//src/python/common:common_dist",
    ],
)
