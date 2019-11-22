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

def load_creds(creds_path: str) -> dict:
    """
    Load the credentials from the .confluence file located in the user's home
    directory
    """
    with open(creds_path) as config:
        creds = yaml.load(config, Loader=yaml.BaseLoader)

    return creds

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
    push html content to confluence page
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

    print(response.text)

def main(args):
    """
    Application entrypoint
    """
    creds = load_creds(str(pathlib.Path.home()) + "/.confluence")

    markdown = get_markdown(args.mdfile)

    html = markdown2.markdown(markdown)

    push_to_confluence(args.space,
                       args.parentid,
                       html,
                       creds['url'] + 'content/',
                       (creds['user'], creds['key']))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert markdown to confluence")
    parser.add_argument('parentid')
    parser.add_argument('space')
    parser.add_argument('mdfile')
    parser.add_argument('--title')

    args = parser.parse_args()

    main(args)
