Markdown To Confluence
======================
This small application takes a markdown file, confluence credentials, (parent)
page and space and converts the markdown to HTML then uploads that to
confluence (where you specified with page and space).

Dependencies
------------
### System
- Python 3.5+
- Confluence Cloud API
- Virtualenv

### Software
- requests
- markdown2
- beautifulsoup4

Development
-----------
You can setup a personal space on your confluence account and use that as your
space.  It will start with a `~`

Deployment
----------
### Setup the python envrionment
1. `virtualenv .venv`
2. `source .venv/bin/activate`
3. `python3 -mpip install -r requirements.txt`

### Setup the configuration file
Follow the `confluence.example.conf` and set up your credentials/URL.

It should be copied to your home directory: `~/.confluence`

You can generate a token by following the instructions found here:
https://confluence.atlassian.com/cloud/api-tokens-938839638.html

That token will be the `key` field in the config.

### Defining page and space aliases
The page and space alias structures in the configuration allow you to define
some friendly, human-readable names for spaces and pages as defined in your
confluence instance.

When doing matching, it will check both the aliases and the id, so if you wanted
to use the ids directly, you would be able to.

You can use something like the following snippet to get the keys and names for
the given spaces in your instance:
`curl -u <creds> -X GET -H "Content-Type: application/json" https://<yourdomainname>/wiki/rest/api/space/ | jq '.results[] | {id: (.id), key: (.key), name: (.name)}'`

Usage
-----
`python3 <parentpage> <space> <markdown_path>`

Testing
-------
TODO:

Notes
-----
1. Even though in the configuration it's called an id, the confluence name for
the space identifiter is a 'key'.
