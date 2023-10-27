python_sources(
    dependencies=[
        "//3rdparty/python#google-cloud-storage",
    ]
)

pex_binary(
    name="sitemap_main",
    entry_point="main.py",
    dependencies=[
        "//3rdparty/python#google-cloud-storage",
    ]
)

python_distribution(
    name="sitemap_dist",
    dependencies=[
        ":sitemap",
    ],
    provides=python_artifact(
        name="sitemap_dist",
        version="1.0",
    ),
    wheel_config_settings={"--global-option": ["--python-tag", "py38"]},
)

docker_image(
    name="sitemap_runner",
    dependencies=[
        ":sitemap",
        ":sitemap_dist",
        "//src/protos:protos_dist",
        "//src/python/common:common_dist",
    ],
)
