"""
License: None
Author: Alan Drees
Purpose: Put a markdown file right into confluence using
native markup
"""

import markdown2
import requests
import argparse
import bs4
import json
import yaml
import pathlib
import sys

"""
Confluence cloud API reference:
https://developer.atlassian.com/cloud/confluence/rest/

Generate an API Access token:
https://confluence.atlassian.com/cloud/api-tokens-938839638.html
"""

"""
TODO:
- implement friendlier space name resolution (use friendly names, resolve to
IDs in the background)
"""

def load_config(creds_path: str) -> dict:
    """
    Load the config from the specified config path
    directory
    """
    with open(creds_path) as config:
        config_struct = yaml.load(config, Loader=yaml.BaseLoader)

    return config_struct

def get_markdown(path: str) -> str:
    """
    Get the Markdown from a specified file
    """
    file_contents = ''

    with open(path) as md_file:
        file_contents = md_file.read()

    return file_contents

def get_title_from_html(parsed_html: bs4.BeautifulSoup) -> str:
    """
    Return the title from the html page
    """
    return parsed_html.find('h1').text

def push_to_confluence(space: str,
                       parentid: str,
                       html_content: str,
                       url: str,
                       auth: str) -> None:
    """
    Push HTML content to confluence page
    """
    parsed_html = bs4.BeautifulSoup(html_content, features="html.parser")

    title = get_title_from_html(parsed_html)

    parsed_html.find('h1').decompose()

    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    payload = json.dumps( {
        "title": title,
        "type": "page",
        "space": {
            "key": space
        },
        "status": "current",
        "ancestors": [{ "id": parentid }],
        "body": {
            "storage": {
                "value": str(parsed_html),
                "representation": "storage"
                }
            }
        })

    response = requests.request(
        "post",
        url,
        data=payload,
        headers=headers,
        auth=auth
    )

    return(response)

def resolve_space(space: str , list_input: list) -> str:
    """
    Resolve a user-friendly string into a space key to be
    passed as the space.key parameter
    """
    return _resolv_func(space, list_input)

def resolve_parent(parent: str , list_input: list) -> str:
    """
    Resolve a user-friendly string into a parent id to be
    passed as the ancestors.id parameter
    """
    return _resolv_func(parent, list_input)

def _resolv_func(i: str, ls: list) -> str:
    """
    Find an entry or return the default in the name/key structures
    """
    for x in ls:
        if i in x['names']:
            return x['id']
        if i == x['id']:
            return x['id']

    return i

def main(args):
    """
    Application entrypoint
    """
    config = load_config(str(pathlib.Path.home()) + "/.confluence")

    markdown = get_markdown(args.mdfile)

    html = markdown2.markdown(markdown)

    auth = (config['user'], config['key'])

    space = resolve_space(args.space, config['spaces'])

    parent = resolve_parent(args.parent, config['pages'])

    response = push_to_confluence(space,
                                  parent,
                                  html,
                                  config['url'] + 'content/',
                                  auth)

    print(response.text)

    if response.ok:
        return 0
    else:
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert markdown to confluence")
    parser.add_argument('parent')
    parser.add_argument('space')
    parser.add_argument('mdfile')
    parser.add_argument('--title')

    args = parser.parse_args()

    sys.exit(main(args))
