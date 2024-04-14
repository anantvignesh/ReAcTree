import re

def clean_yaml(raw):
    try:
        # This pattern matches the variations of the "```yaml" prefix and the closing "```
        # It handles optional spaces and the case-insensitivity of the "yaml" part.
        pattern = r'```(?:yaml\s?|YAML\s?)?\n?'
        # Using re.sub to replace the matched patterns with an empty string.
        clean = re.sub(pattern, '', raw, flags=re.IGNORECASE)
        # Removing the trailing "```" if it exists
        clean = re.sub(r'```$', '', clean)
        return clean
    except:
        return raw

def clean_xml(raw):
    pattern = r'```(?:xml\s?|XML\s?)?\n?'
    try:
        clean = re.sub(pattern, '', raw, flags=re.IGNORECASE)
        clean = re.sub(r'```$', '', clean)
        return clean
    except:
        return raw

def clean_sql(raw):
    pattern = r'```(?:sql\s?|SQL\s?)?\n?'
    try:
        clean = re.sub(pattern, '', raw, flags=re.IGNORECASE)
        clean = re.sub(r'```$', '', clean)
        return clean
    except:
        return raw