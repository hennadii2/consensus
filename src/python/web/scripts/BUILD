python_sources(
    dependencies=[
        "//src/mock_data:mock_data",
        "//src/infra/db:main_sql",
        "//3rdparty/python#GitPython",
        "//src/python/web:local_dev_env",
    ]
)

pex_binary(
    name="ingest_mock_data",
    entry_point="ingest_mock_data.py",
)

pex_binary(
    name="add_users_csv_to_allowlist",
    entry_point="add_users_csv_to_allowlist.py",
)

pex_binary(
    name="push_web_cms_data_to_blob",
    entry_point="push_web_cms_data_to_blob.py",
    dependencies=[
      "//data/web:web",
    ]
)

pex_binary(
    name="check_prod_sitemap",
    entry_point="check_prod_sitemap.py",
)

pex_binary(
    name="install_web_backend_models",
    entry_point="install_web_backend_models.py",
)

pex_binary(
    name="install_web_services_models",
    entry_point="install_web_services_models.py",
)

pex_binary(
    name="install_web_chat_gpt_plugin_models",
    entry_point="install_web_chat_gpt_plugin_models.py",
)

pex_binary(
    name="time_metadata_sort",
    entry_point="time_metadata_sort.py",
)

pex_binary(
    name="populate_subscription_products_table",
    entry_point="populate_subscription_products_table.py",
)

pex_binary(
    name="migrate_ltd",
    entry_point="migrate_ltd.py",
)

pex_binary(
    name="map_stripe_clerk",
    entry_point="map_stripe_clerk.py",
)

pex_binary(
    name="append_portal_link",
    entry_point="append_portal_link.py",
)
