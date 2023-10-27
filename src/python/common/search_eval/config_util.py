import sys
from dataclasses import asdict as dataclass_to_dict

import common.storage.gcs_util as gcs_util
from common.search.search_util import DEFAULT_SEARCH_CONFIG, SortParams
from common.storage.connect import StorageClient
from ruamel.yaml import YAML


# could make this a singleton class i guess but meh
def _get_yaml_object():
    yaml = YAML(typ="safe")
    yaml.default_flow_style = False
    return yaml


def get_sort_params(config: dict) -> SortParams:
    config_sort_params = config.get("sort_params", {})
    if not config_sort_params:
        sort_params = DEFAULT_SEARCH_CONFIG.metadata_sort_params
    else:
        # TODO(cvarano): add parameter strings to constants.py
        sort_params = SortParams(
            window_size=config_sort_params.get(
                "window_size", DEFAULT_SEARCH_CONFIG.metadata_sort_params.window_size
            ),
            similarity_weight=config_sort_params.get(
                "similarity_weight", DEFAULT_SEARCH_CONFIG.metadata_sort_params.similarity_weight
            ),
            probability_weight=config_sort_params.get(
                "probability_weight", DEFAULT_SEARCH_CONFIG.metadata_sort_params.probability_weight
            ),
            citation_count_weight=config_sort_params.get(
                "citation_count_weight",
                DEFAULT_SEARCH_CONFIG.metadata_sort_params.citation_count_weight,
            ),
            citation_count_min=config_sort_params.get(
                "citation_count_min", DEFAULT_SEARCH_CONFIG.metadata_sort_params.citation_count_min
            ),
            citation_count_max=config_sort_params.get(
                "citation_count_max", DEFAULT_SEARCH_CONFIG.metadata_sort_params.citation_count_max
            ),
            publish_year_weight=config_sort_params.get(
                "publish_year_weight",
                DEFAULT_SEARCH_CONFIG.metadata_sort_params.publish_year_weight,
            ),
            publish_year_min=config_sort_params.get(
                "publish_year_min", DEFAULT_SEARCH_CONFIG.metadata_sort_params.publish_year_min
            ),
            publish_year_max=config_sort_params.get(
                "publish_year_max", DEFAULT_SEARCH_CONFIG.metadata_sort_params.publish_year_max
            ),
            best_quartile_weight=config_sort_params.get(
                "best_quartile_weight",
                DEFAULT_SEARCH_CONFIG.metadata_sort_params.best_quartile_weight,
            ),
            best_quartile_default=config_sort_params.get(
                "best_quartile_default",
                DEFAULT_SEARCH_CONFIG.metadata_sort_params.best_quartile_default,
            ),
        )
    # Store the sort params in the config for tracking purposes;
    # the whole config will be uploaded to GCS with each experiment.
    config["sort_params"] = dataclass_to_dict(sort_params)
    return sort_params


def load_yaml_config(config_path: str, config_tag: str) -> dict:
    """
    Load a yaml config file and return the values for the given configuration tag.
    """
    yaml = _get_yaml_object()
    with open(config_path, "r") as f:
        full_config = yaml.load(f)
    if config_tag not in full_config:
        raise ValueError(f"Tag {config_tag} not found in config file {config_path}")
    config = full_config[config_tag]
    config["tag"] = config_tag
    return config  # type: ignore [no-any-return]


def write_yaml_config_to_gcs(storage_client: StorageClient, config: dict, run_id: str):
    # TODO(cvarano): parameterize local path
    # gcs api expects a filepath, so we write locally first
    yaml_path = f"{run_id}.yaml"
    with open(yaml_path, "w") as f:
        yaml = _get_yaml_object()
        yaml.dump(config, f)
    gcs_util.upload_search_eval_metrics_yaml_config(storage_client, yaml_path, run_id)


# primarily for debugging
def pretty_print_yaml_config(config: dict):
    yaml = _get_yaml_object()
    yaml.dump(config, sys.stdout)
