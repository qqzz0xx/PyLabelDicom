import os.path as osp
import json

here = osp.dirname(osp.abspath(__file__))


def get_default_config():
    config = {}

    config['tags'] = get_tags_config()
    config['keymap'] = get_keymap_config()

    return config


def get_tags_config():
    config = None
    tag_config_file = osp.join(here, 'tags.json')
    with open(tag_config_file) as f:
        config = json.load(f)

    return config


def get_keymap_config():
    config = None
    tag_config_file = osp.join(here, 'keymap.json')
    with open(tag_config_file) as f:
        config = json.load(f)

    return config
