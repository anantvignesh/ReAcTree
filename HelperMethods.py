import re
import json
from typing import Any, Dict

def clean_code_block(raw: str, language: str = None) -> str:
    """
    Cleans code blocks from a raw string, optionally specifying the language.

    Args:
        raw (str): The raw string containing the code block.
        language (str, optional): The language identifier (e.g., 'json', 'yaml', 'xml', 'sql').

    Returns:
        str: The cleaned code block.
    """
    try:
        if language:
            pattern = rf'```(?:{language}\s?|{language.upper()}\s?)?\n?'
        else:
            pattern = r'```(?:\w*\s?)?\n?'
        clean = re.sub(pattern, '', raw, flags=re.IGNORECASE | re.MULTILINE)
        clean = re.sub(r'```$', '', clean)
        return clean.strip()
    except:
        return raw.strip()

def clean_yaml(raw: str) -> str:
    """
    Cleans YAML code blocks from a raw string.

    Args:
        raw (str): The raw string containing the YAML code block.

    Returns:
        str: The cleaned YAML string.
    """
    return clean_code_block(raw, 'yaml')

def clean_xml(raw: str) -> str:
    """
    Cleans XML code blocks from a raw string.

    Args:
        raw (str): The raw string containing the XML code block.

    Returns:
        str: The cleaned XML string.
    """
    return clean_code_block(raw, 'xml')

def clean_sql(raw: str) -> str:
    """
    Cleans SQL code blocks from a raw string.

    Args:
        raw (str): The raw string containing the SQL code block.

    Returns:
        str: The cleaned SQL string.
    """
    return clean_code_block(raw, 'sql')

def clean_json(raw: str) -> str:
    """
    Cleans JSON code blocks from a raw string and normalizes the JSON string.

    Args:
        raw (str): The raw string containing the JSON code block.

    Returns:
        str: The cleaned and normalized JSON string.
    """
    cleaned = clean_code_block(raw, 'json')
    try:
        # Load and dump to normalize the JSON string
        json_object = json.loads(cleaned)
        cleaned = json.dumps(json_object)
        return cleaned
    except json.JSONDecodeError:
        return cleaned

def validate_json(json_string: str) -> bool:
    """
    Validates if the input string is valid JSON.

    Args:
        json_string (str): The JSON string to validate.

    Returns:
        bool: True if valid JSON, False otherwise.
    """
    try:
        json.loads(json_string)
        return True
    except ValueError:
        return False

def pretty_print_json(json_string: str) -> str:
    """
    Pretty-prints a JSON string.

    Args:
        json_string (str): The JSON string to format.

    Returns:
        str: The pretty-printed JSON string.
    """
    try:
        json_object = json.loads(json_string)
        pretty_json = json.dumps(json_object, indent=2)
        return pretty_json
    except ValueError:
        return json_string

def extract_text_between_tags(text: str, tag: str) -> str:
    """
    Extracts text between specified XML tags.

    Args:
        text (str): The text containing XML tags.
        tag (str): The tag to extract text from.

    Returns:
        str: The extracted text.
    """
    pattern = rf'<{tag}>(.*?)</{tag}>'
    matches = re.findall(pattern, text, re.DOTALL)
    return matches[0] if matches else ''

def remove_html_tags(text: str) -> str:
    """
    Removes HTML tags from a string.

    Args:
        text (str): The text containing HTML tags.

    Returns:
        str: The text without HTML tags.
    """
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def sanitize_input(text: str) -> str:
    """
    Sanitizes input text by escaping special characters.

    Args:
        text (str): The input text to sanitize.

    Returns:
        str: The sanitized text.
    """
    return re.escape(text)

def merge_dictionaries(dict1: Dict[Any, Any], dict2: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Merges two dictionaries.

    Args:
        dict1 (Dict[Any, Any]): The first dictionary.
        dict2 (Dict[Any, Any]): The second dictionary.

    Returns:
        Dict[Any, Any]: The merged dictionary.
    """
    merged = dict1.copy()
    merged.update(dict2)
    return merged

def flatten_json(y: Dict[Any, Any], separator: str = '.') -> Dict[str, Any]:
    """
    Flattens a nested JSON/dictionary.

    Args:
        y (Dict[Any, Any]): The JSON/dictionary to flatten.
        separator (str, optional): The separator between keys.

    Returns:
        Dict[str, Any]: The flattened dictionary.
    """
    out = {}

    def flatten(x: Any, name: str = ''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], f"{name}{a}{separator}")
        elif type(x) is list:
            for i, a in enumerate(x):
                flatten(a, f"{name}{i}{separator}")
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

def generate_unique_id(prefix: str = '', length: int = 8) -> str:
    """
    Generates a unique identifier.

    Args:
        prefix (str, optional): The prefix for the ID.
        length (int, optional): The length of the random part of the ID.

    Returns:
        str: The unique identifier.
    """
    import uuid
    unique_id = prefix + uuid.uuid4().hex[:length]
    return unique_id