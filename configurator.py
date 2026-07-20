import yaml
import numpy as np
from pprint import pprint
import json

# load yaml file


def config_loader(config_file="zones.yaml"):
    with open(config_file, "r") as f:
        config = yaml.load(f, Loader=yaml.UnsafeLoader)
    zone_in = [zone_in["input_zone"] for zone_in in config]
    zone_out = [zone_out["output_zone"] for zone_out in config]
    return zone_in, zone_out


def json_conf_loader(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)

    zone = {"location": config["location"]}
    zone["entry_zone"] = np.array([[x["x"], x["y"]] for x in config["entry_zone"]])
    zone["exit_zone"] = np.array([[x["x"], x["y"]] for x in config["exit_zone"]])
    zone["counter_zone"] = np.array([[x["x"], x["y"]] for x in config["counter_zone"]])
    if "test_video" in config:
        zone["test_video"] = config["test_video"]
    return zone
