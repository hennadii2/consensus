python_sources(
    dependencies=[
        "//3rdparty/python#google-cloud-storage",
        "//3rdparty/python#pandas",
        "//3rdparty/python#google-apitools",
        "//3rdparty/python#openpyxl",
        "//3rdparty/python#fsspec",
        "//3rdparty/python#gcsfs",
    ]
)

pex_binary(
    name="compute_journal_scores_main",
    entry_point="main.py",
    dependencies=[
        "//3rdparty/python#google-cloud-storage",
        "//3rdparty/python#pandas",
        "//3rdparty/python#google-apitools",
        "//3rdparty/python#openpyxl",
        "//3rdparty/python#fsspec",
        "//3rdparty/python#gcsfs",
    ]
)

python_distribution(
    name="compute_journal_scores_dist",
    dependencies=[
        ":compute_journal_scores",
    ],
    provides=python_artifact(
        name="compute_journal_scores_dist",
        version="1.0",
    ),
    wheel_config_settings={"--global-option": ["--python-tag", "py38"]},
)

docker_image(
    name="compute_journal_scores_runner",
    dependencies=[
        ":compute_journal_scores",
        ":compute_journal_scores_dist",
        "//src/protos:protos_dist",
        "//src/python/common:common_dist",
    ],
)
