import os.path as osp
import json

here = osp.dirname(osp.abspath(__file__))


def get_default_config():
    config = {}
    tag_config_file = osp.join(here, 'tags.json')
    with open(tag_config_file) as f:
        config['tags'] = json.load(f)

    return config
