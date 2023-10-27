python_sources(
    dependencies=[
        "//3rdparty/python#google-cloud-storage",
    ]
)

pex_binary(
    name="parse_into_dataset_main",
    entry_point="main.py",
    dependencies=[
        "//3rdparty/python#google-cloud-storage",
    ]
)

python_distribution(
    name="parse_into_dataset_dist",
    dependencies=[
        ":parse_into_dataset",
    ],
    provides=python_artifact(
        name="parse_into_dataset_dist",
        version="1.0",
    ),
    wheel_config_settings={"--global-option": ["--python-tag", "py38"]},
)

docker_image(
    name="parse_into_dataset_runner",
    dependencies=[
        ":parse_into_dataset",
        ":parse_into_dataset_dist",
        "//src/protos:protos_dist",
        "//src/mock_data:mock_data",
        "//src/python/common:common_dist",
    ],
)
