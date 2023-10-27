files(
    name="analytics_proxy_sources",
    sources=["nginx/default.conf"],
)

docker_image(
    name="analytics_proxy",
    image_tags=["{build_args.GIT_COMMIT}", "{build_args.LATEST_BRANCH_TAG}"],
    dependencies=[
        ":analytics_proxy_sources",
    ]
)
