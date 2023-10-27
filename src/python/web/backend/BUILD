python_sources(
    name="backend_sources",
    sources=["app/*.py", "app/common/**/*.py", "app/common/test/*.py", "app/endpoints/**/*.py", "app/middleware/**/*.py"]
)

python_tests(
    name="tests",
    dependencies=[
        "//data/web:web",
        "//3rdparty/python#httpx",
    ],
    sources=["app/common/**/*_test.py", "app/endpoints/**/*_test.py"]
)

pex_binary(
    name="backend",
    entry_point="app/main.py",
    dependencies=[
        ":backend_sources",
    ],
)

python_distribution(
    name="backend_dist",
    dependencies=[
        ":backend_sources",
    ],
    provides=python_artifact(
        name="backend_dist",
        version="1.0",
    ),
    wheel_config_settings={"--global-option": ["--python-tag", "py37"]},
)

docker_image(
    name="web_backend",
    image_tags=["{build_args.GIT_COMMIT}", "{build_args.LATEST_BRANCH_TAG}"],
    dependencies=[
        ":backend",
        ":backend_dist",
    ]
)
