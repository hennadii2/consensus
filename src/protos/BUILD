protobuf_sources(
    python_source_root="src/python",
    dependencies=[
        "//3rdparty/python#protobuf",
    ]
)

python_distribution(
    name="protos_dist",
    dependencies=[
        ":protos",
    ],
    provides=python_artifact(
        name="protos_dist",
        version="1.0",
    ),
    wheel_config_settings={"--global-option": ["--python-tag", "py38"]},
)
