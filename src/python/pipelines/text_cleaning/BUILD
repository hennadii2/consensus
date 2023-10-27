python_sources(
    dependencies=[
        "//3rdparty/python#google-cloud-storage",
    ]
)

pex_binary(
    name="text_cleaning_main",
    entry_point="main.py",
    dependencies=[
        "//3rdparty/python#google-cloud-storage",
    ]
)

python_distribution(
    name="text_cleaning_dist",
    dependencies=[
        ":text_cleaning",
    ],
    provides=python_artifact(
        name="text_cleaning_dist",
        version="1.0",
    ),
    wheel_config_settings={"--global-option": ["--python-tag", "py38"]},
)

docker_image(
    name="text_cleaning_runner",
    dependencies=[
        ":text_cleaning",
        ":text_cleaning_dist",
        "//src/protos:protos_dist",
        "//src/mock_data:mock_data",
        "//src/python/common:common_dist",
    ],
)
