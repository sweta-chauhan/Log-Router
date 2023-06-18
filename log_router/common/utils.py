from typing import Dict, Generator, List


def flatten_dict(dictionary: Dict, delimiter: str = ".") -> Dict:
    """

    Converts nested dictionary to single level dict with delimited keys with the specified delimiter.
    :examples:
        >>> dictionary = {'data':{0:{'x0':['Missing data for required field.'],'x1':{'2':{'key': \
        ['Must be one of: 4, 7']}}}}}
        >>> flatten_dict(dictionary)
        {'data.0.x0': ['Missing data for required field.'], 'data.0.x1.2.key': ['Must be one of: 4, 7']}
    """
    flat_dict = dict()
    for key, value in dictionary.items():
        if isinstance(value, dict):
            flatten_value_dict = flatten_dict(value, delimiter=delimiter)
            for k, v in flatten_value_dict.items():
                flat_dict[f"{key}{delimiter}{k}"] = v
        else:
            flat_dict[key] = value
    return flat_dict


def generate_error_list(messages: dict) -> list:
    """
    Converts marshmallow ValidationError messages to list of dictionaries
    :param messages:
    :return:
    :examples:
        >>> error_messages = {'data':{0:{'x0':['Missing data for required field.'],'x1':{'2':{'key':['Must be one of: 4, 7']}}}}}
        >>> generate_error_list(error_messages)
        [{'type': 'SchemaValidationError', 'value': 'x0', 'message': 'Missing data for required field.'}, {'type': 'SchemaValidationError', 'value': 'key', 'message': 'Must be one of: 4, 7'}]

    """
    delimiter = "."
    flattened_messages = flatten_dict(messages, delimiter=delimiter)
    error_list = [
        {
            "type": "SchemaValidationError",
            "value": key.split(delimiter)[-1],
            "message": value[0],
        }
        for key, value in flattened_messages.items()
    ]
    return error_list


def chunks(data: List, chunk_size: int) -> Generator[List, None, None]:
    """
    Generator function that converts supplied list into smaller lists of 'chunk_size' length and yields
    each list.
    :examples:
        >>> list(chunks([1,2,3,4,5], 2))
        [[1, 2], [3, 4], [5]]
        >>> list(chunks([1,2,3], 10))
        [[1, 2, 3]]
    """
    max_size = len(data)
    if chunk_size > max_size:
        chunk_size = max_size
    for index in range(0, max_size, chunk_size):
        yield data[index : index + chunk_size]
