import configparser
import os

config = configparser.ConfigParser()
config.read('user_script.ini')
sections = config.sections()
for section in sections:
    section_dict = dict(config[section])
    sorted_keys =sorted(section_dict.keys(), key=lambda x:x.lower())
