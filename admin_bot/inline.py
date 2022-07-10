from random import choice
import datetime
import os
from telegram import ReplyKeyboardMarkup, KeyboardButton
import configparser

def get_ini_keyboard() -> ReplyKeyboardMarkup:
    files = os.listdir('./config_files')
    buttons = []
    for file in files:
        buttons.append([file])
    return ReplyKeyboardMarkup(
            buttons, 
            resize_keyboard=True, 
            one_time_keyboard=True
            )

def get_sections_keyboard(config) -> ReplyKeyboardMarkup:
    config_parser = configparser.ConfigParser(allow_no_value=True, delimiters="=")
    config_parser.optionxform = str
    config_parser.read(os.path.join("./config_files", config), encoding='utf-8')
    sections = config_parser.sections()
    buttons = []
    for section in sections:
        buttons.append([section])
    return ReplyKeyboardMarkup(
        buttons, 
        resize_keyboard=True, one_time_keyboard=True, 
        input_field_placeholder="Choose a section"
        )

def section_details(config, section):
    config_parser = configparser.ConfigParser(allow_no_value=True, delimiters="=")
    config_parser.optionxform = str
    config_parser.read(os.path.join("./config_files/", config))
    my_dict = dict(config_parser[section])
    str1 = "\n"
    for key,value in my_dict.items():
        str1 += key + ((" : " + value+"\n") if value != None else "\n" + "\n")
    return str1

def add_or_remove_option(config, op, section, key, value=None):
    final_value=""
    if value != None:
        value_with_underscore = value.replace(" ", "_")
        final_value = value_with_underscore.replace("\n", "#")
    key_with_underscore = key.replace(" ", "_")
    final_key = key_with_underscore.replace("\n",
    "#")
    config_parser = configparser.ConfigParser(allow_no_value=True, delimiters="=")
    config_parser.optionxform = str
    file_name = os.path.join("./config_files/", config)
    config_parser.read(file_name)
    if op == "add":
        config_parser.set(section, key, value)
        # write into the log file
        if os.path.exists('./admin_bot/undo_log.txt'):
            with open('./admin_bot/undo_log.txt', 'a') as logfile:
                dummy = "\n{} User added {}={} to section {} of {}".format(
                    datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"), 
                    final_key,
                    final_value,
                    section,
                    config,
                    )
                logfile.write(dummy)
        else:
            with open('./admin_bot/undo_log.txt', 'x') as logfile:
                dummy = "\n{} User added {}={} to section {} of {}".format(
                    datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"), 
                    final_key,
                    final_value,
                    section,
                    config,
                    )
                logfile.write(dummy)
    if op == "remove": 
        # write into the log file
        removed_value_with_underscore = config_parser.get(section,key).replace(" ", "_")
        removed_value = removed_value_with_underscore.replace("\n","#")
        if os.path.exists('./admin_bot/undo_log.txt'):
            with open('./admin_bot/undo_log.txt', 'a') as logfile:
                dummy = "\n{} User removed {}={} from section {} of {}".format(
                datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"), 
                final_key, 
                removed_value, 
                section,
                config,
                )
                logfile.write(dummy)
        else:
            with open('./admin_bot/undo_log.txt', 'x') as logfile:
                dummy = "\n{}     User removed {} = {} from section {} of {}".format(
                datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"), 
                final_key, 
                removed_value, 
                section,
                config,
                )
                logfile.write(dummy)
        config_parser.remove_option(section, key)
    elif op == "edit":
        # write into the log file
        removed_value_with_underscore = config_parser.get(section,key).replace(" ", "_")
        removed_value = removed_value_with_underscore.replace("\n","#")
        if os.path.exists('./admin_bot/undo_log.txt'):
            with open('./admin_bot/undo_log.txt', 'a') as logfile:
                dummy = "\n{} User edited {}={} to {}={} from section {} of {}".format(
                datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"), 
                final_key,
                removed_value,
                final_key, 
                final_value,  # new value
                section,
                config,
                )
                logfile.write(dummy)
        else:
            with open('./admin_bot/undo_log.txt', 'x') as logfile:
                dummy = "\n{}     User removed {} = {} from section {} of {}".format(
                datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"), 
                final_key,
                removed_value,
                final_key, 
                final_value,  # new value
                section,
                config,
                )
                logfile.write(dummy)
        config_parser.set(section, key, value)
        
    with open(file_name, "w+") as file:
        config_parser.write(file)

def revert(undo_string):
    arguments = (undo_string.split("User")[1].strip()).split()
    config_parser = configparser.ConfigParser(allow_no_value=True, delimiters="=")
    config_parser.optionxform = str
    config = arguments[-1]
    file_name = os.path.join("./config_files/", config)
    config_parser.read(file_name)
    if arguments[0] == "added":
        arguments = [e for e in arguments if e not in ('to', 'section', 'of')]
        #the result would be [added, key=value, section, filename]
        key_with_underscore_and_sharp = (arguments[1].split("="))[0]
        key_with_underscore = key_with_underscore_and_sharp.replace("#", "\n")
        key = key_with_underscore.replace("_", " ")
        section = arguments[2]
        config_parser.remove_option(section, key)
    if arguments[0] == "removed":
        arguments = [e for e in arguments if e not in ('from', 'section', 'of')]
        # the result would become [removed, key=value, section, filename]
        key_value_pair = arguments[1].split("=")
        key_with_sharp = key_value_pair[0].replace("_", " ")
        key = key_with_sharp.replace("#", "\n")
        value_with_sharp = key_value_pair[1].replace("_", " ")
        value = value_with_sharp.replace("#", "\n")
        section = arguments[2]
        config_parser.set(section, key, value)
    if arguments[0] == "edited":
        arguments = [e for e in arguments if e not in ('from', 'section', 'of', 'to')]
        #the result would be [edited, prev_key=prev_val, new_key=new_val, section, filename]
        prev_key_value_pair = arguments[1].split("=")
        prev_key_with_sharp = prev_key_value_pair[0].replace("_", " ")
        prev_key = prev_key_with_sharp.replace("#","\n")
        prev_value_with_sharp = prev_key_value_pair[1].replace("_", " ")
        prev_value = prev_value_with_sharp.replace("#","\n")
        section = arguments[3]
        config_parser.set(section, prev_key, prev_value)
    with open(file_name, "w+") as file:
        config_parser.write(file)
