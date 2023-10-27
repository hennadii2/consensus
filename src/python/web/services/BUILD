python_sources(
    name="services_api",
    sources=["api.py",]
)

python_sources(
    name="services_sources",
    sources=["app/*.py", "app/endpoints/**/*.py",]
)

pex_binary(
    name="services",
    entry_point="app/main.py",
    dependencies=[
        ":services_sources",
    ],
)

python_distribution(
    name="services_dist",
    dependencies=[
        ":services_sources",
    ],
    provides=python_artifact(
        name="services_dist",
        version="1.0",
    ),
    wheel_config_settings={"--global-option": ["--python-tag", "py37"]},
)

docker_image(
    name="web_services",
    image_tags=["{build_args.GIT_COMMIT}", "{build_args.LATEST_BRANCH_TAG}"],
    dependencies=[
        ":services",
        ":services_dist",
    ]
)
