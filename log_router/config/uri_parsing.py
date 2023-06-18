import re
from urllib import parse


def parse_connection_string(connection_string):
    parsed_string = parse.urlparse(connection_string)
    try:
        scheme, user, password, host, port, database = re.match(
            "(.*?)://(.*?):(.*?)@(.*?):(.*?)/(.*)[/]?", connection_string
        ).groups()
        name = database
        if "/" in database:
            name = database.split("/")[0]
    except:
        name = parsed_string.path.lstrip("/")
        host = parsed_string.hostname
        port = parsed_string.port
        user = parsed_string.username
        password = parsed_string.password

    param_dict = dict(parse.parse_qsl(parsed_string.query))

    db_config = {
        "host": host,
        "username": user,
        "password": password,
        "port": port,
        "name": name,
        "params": param_dict,
        "uri": connection_string,
    }
    return db_config
