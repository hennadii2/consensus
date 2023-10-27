python_sources(
    name="chat_gpt_plugin_sources",
    sources=["app/*.py", "app/common/**/*.py", "app/endpoints/**/*.py",]
)

python_tests(
    name="tests",
    sources=["app/endpoints/**/*_test.py"]
)

files(
    name="static_files",
    sources=["app/public/**/*"]
)

pex_binary(
    name="chat_gpt_plugin",
    entry_point="app/main.py",
    dependencies=[
        ":chat_gpt_plugin_sources",
    ],
)

python_distribution(
    name="chat_gpt_plugin_dist",
    dependencies=[
        ":chat_gpt_plugin_sources",
    ],
    provides=python_artifact(
        name="chat_gpt_plugin_dist",
        version="1.0",
    ),
    wheel_config_settings={"--global-option": ["--python-tag", "py37"]},
)

docker_image(
    name="web_chat_gpt_plugin",
    image_tags=["{build_args.GIT_COMMIT}", "{build_args.LATEST_BRANCH_TAG}"],
    dependencies=[
        ":static_files",
        ":chat_gpt_plugin",
        ":chat_gpt_plugin_dist",
    ]
)
