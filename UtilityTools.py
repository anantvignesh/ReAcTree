import math
import requests
import json
from typing import List, Dict, Any, Tuple
from datetime import datetime
import uuid

def calculator(expression: str) -> float:
    """
    Evaluates a mathematical expression safely.

    Args:
        expression (str): The mathematical expression to evaluate.

    Returns:
        float: The result of the calculation.
    """
    try:
        # Define allowed names
        allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith("__")
        }
        # Compile the expression
        code = compile(expression, "<string>", "eval")
        # Check for disallowed names
        for name in code.co_names:
            if name not in allowed_names:
                raise NameError(f"The use of '{name}' is not allowed.")
        result = eval(code, {"__builtins__": {}}, allowed_names)
        return result
    except Exception as e:
        raise ValueError(f"Calculation error: {e}")

def web_search(query: str) -> str:
    """
    Performs a web search and returns summarized results.

    Args:
        query (str): The search query.

    Returns:
        str: The summary of search results.
    """
    try:
        # Note: Replace 'YOUR_API_KEY' and 'YOUR_SEARCH_ENGINE_ID' with actual values.
        api_key = 'YOUR_API_KEY'
        search_engine_id = 'YOUR_SEARCH_ENGINE_ID'
        url = 'https://www.googleapis.com/customsearch/v1'
        params = {'key': api_key, 'cx': search_engine_id, 'q': query}
        response = requests.get(url, params=params)
        data = response.json()
        snippets = [item['snippet'] for item in data.get('items', [])]
        summary = ' '.join(snippets[:3])  # Return first 3 snippets
        return summary if summary else "No results found."
    except Exception as e:
        raise ValueError(f"Web search error: {e}")

def unit_converter(value: float, from_unit: str, to_unit: str) -> str:
    """
    Converts units from one type to another.

    Args:
        value (float): The numerical value to convert.
        from_unit (str): The unit of the input value.
        to_unit (str): The unit to convert to.

    Returns:
        str: The result of the conversion.
    """
    try:
        import pint
        ureg = pint.UnitRegistry()
        quantity = value * ureg(from_unit)
        converted = quantity.to(to_unit)
        return f"{quantity} = {converted}"
    except Exception as e:
        raise ValueError(f"Conversion error: {e}")

def translate_text(text: str, target_language: str) -> str:
    """
    Translates text to the specified language.

    Args:
        text (str): The text to translate.
        target_language (str): The target language code (e.g., 'en', 'fr', 'es').

    Returns:
        str: The translated text.
    """
    try:
        # Note: This is a placeholder. Replace with an actual translation API.
        # Example using Google Translate API.
        from googletrans import Translator
        translator = Translator()
        translation = translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        raise ValueError(f"Translation error: {e}")

def summarize_text(text: str) -> str:
    """
    Summarizes the given text.

    Args:
        text (str): The text to summarize.

    Returns:
        str: The summary of the text.
    """
    try:
        # Simple summarization by extracting key sentences.
        from gensim.summarization import summarize
        summary = summarize(text, ratio=0.3)
        return summary
    except Exception as e:
        raise ValueError(f"Summarization error: {e}")

def sentiment_analysis(text: str) -> Dict[str, float]:
    """
    Performs sentiment analysis on the given text.

    Args:
        text (str): The text to analyze.

    Returns:
        Dict[str, float]: The sentiment scores (positive, negative, neutral).
    """
    try:
        from textblob import TextBlob
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        sentiment = {
            'polarity': polarity,
            'subjectivity': subjectivity
        }
        return sentiment
    except Exception as e:
        raise ValueError(f"Sentiment analysis error: {e}")

def current_datetime(timezone: str = 'UTC') -> str:
    """
    Returns the current date and time in the specified timezone.

    Args:
        timezone (str, optional): The timezone identifier.

    Returns:
        str: The current date and time as a string.
    """
    try:
        import pytz
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        return now.strftime('%Y-%m-%d %H:%M:%S %Z%z')
    except Exception as e:
        raise ValueError(f"DateTime error: {e}")

def weather_info(location: str) -> str:
    """
    Retrieves weather information for the specified location.

    Args:
        location (str): The location to get weather information for.

    Returns:
        str: The weather information.
    """
    try:
        # Note: Replace 'YOUR_API_KEY' with your actual OpenWeatherMap API key.
        api_key = 'YOUR_API_KEY'
        params = {'q': location, 'appid': api_key, 'units': 'metric'}
        response = requests.get('http://api.openweathermap.org/data/2.5/weather', params=params)
        data = response.json()
        weather_desc = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"The current weather in {location.title()} is {weather_desc} with a temperature of {temp}°C."
    except Exception as e:
        raise ValueError(f"Weather information error: {e}")

def currency_converter(amount: float, from_currency: str, to_currency: str) -> str:
    """
    Converts currency from one type to another.

    Args:
        amount (float): The amount of money to convert.
        from_currency (str): The currency code of the input amount (e.g., 'USD').
        to_currency (str): The currency code to convert to (e.g., 'EUR').

    Returns:
        str: The result of the conversion.
    """
    try:
        # Note: Replace 'YOUR_API_KEY' with your actual currency conversion API key.
        api_key = 'YOUR_API_KEY'
        url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/{from_currency}'
        response = requests.get(url)
        data = response.json()
        if data['result'] != 'success':
            raise ValueError("Failed to retrieve exchange rates.")
        rate = data['conversion_rates'][to_currency]
        converted_amount = amount * rate
        return f"{amount} {from_currency} = {converted_amount:.2f} {to_currency}"
    except Exception as e:
        raise ValueError(f"Currency conversion error: {e}")

def generate_uuid() -> str:
    """
    Generates a random UUID.

    Returns:
        str: The generated UUID.
    """
    return str(uuid.uuid4())

def random_password(length: int = 12) -> str:
    """
    Generates a random password of specified length.

    Args:
        length (int, optional): The length of the password.

    Returns:
        str: The generated password.
    """
    import random
    import string
    try:
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for i in range(length))
        return password
    except Exception as e:
        raise ValueError(f"Password generation error: {e}")

def fetch_wikipedia_summary(topic: str) -> str:
    """
    Fetches a summary of a topic from Wikipedia.

    Args:
        topic (str): The topic to search for.

    Returns:
        str: The summary of the Wikipedia article.
    """
    try:
        import wikipedia
        summary = wikipedia.summary(topic, sentences=3)
        return summary
    except Exception as e:
        raise ValueError(f"Wikipedia error: {e}")

def encode_base64(text: str) -> str:
    """
    Encodes text to Base64.

    Args:
        text (str): The text to encode.

    Returns:
        str: The Base64 encoded string.
    """
    import base64
    try:
        encoded_bytes = base64.b64encode(text.encode('utf-8'))
        encoded_str = encoded_bytes.decode('utf-8')
        return encoded_str
    except Exception as e:
        raise ValueError(f"Base64 encoding error: {e}")

def decode_base64(encoded_text: str) -> str:
    """
    Decodes a Base64 encoded string.

    Args:
        encoded_text (str): The Base64 encoded string.

    Returns:
        str: The decoded text.
    """
    import base64
    try:
        decoded_bytes = base64.b64decode(encoded_text.encode('utf-8'))
        decoded_str = decoded_bytes.decode('utf-8')
        return decoded_str
    except Exception as e:
        raise ValueError(f"Base64 decoding error: {e}")

def json_formatter(json_string: str) -> str:
    """
    Formats a JSON string for readability.

    Args:
        json_string (str): The JSON string to format.

    Returns:
        str: The formatted JSON string.
    """
    try:
        json_object = json.loads(json_string)
        formatted_json = json.dumps(json_object, indent=2)
        return formatted_json
    except Exception as e:
        raise ValueError(f"JSON formatting error: {e}")

def extract_keywords(text: str) -> List[str]:
    """
    Extracts keywords from the given text.

    Args:
        text (str): The text to extract keywords from.

    Returns:
        List[str]: A list of keywords.
    """
    try:
        import nltk
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(text)
        keywords = [word for word in words if word.isalnum() and word.lower() not in stop_words]
        return keywords
    except Exception as e:
        raise ValueError(f"Keyword extraction error: {e}")

def html_to_text(html_content: str) -> str:
    """
    Converts HTML content to plain text.

    Args:
        html_content (str): The HTML content.

    Returns:
        str: The plain text extracted from the HTML.
    """
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        return text
    except Exception as e:
        raise ValueError(f"HTML to text conversion error: {e}")

def parse_csv(csv_content: str) -> List[Dict[str, Any]]:
    """
    Parses CSV content into a list of dictionaries.

    Args:
        csv_content (str): The CSV content as a string.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing the CSV rows.
    """
    import csv
    from io import StringIO
    try:
        f = StringIO(csv_content)
        reader = csv.DictReader(f)
        data = [row for row in reader]
        return data
    except Exception as e:
        raise ValueError(f"CSV parsing error: {e}")

def generate_qr_code(data: str, filename: str = 'qrcode.png') -> None:
    """
    Generates a QR code from the given data and saves it as an image file.

    Args:
        data (str): The data to encode in the QR code.
        filename (str, optional): The filename for the saved QR code image.

    Returns:
        None
    """
    try:
        import qrcode
        img = qrcode.make(data)
        img.save(filename)
    except Exception as e:
        raise ValueError(f"QR code generation error: {e}")

def read_qr_code(image_path: str) -> str:
    """
    Reads a QR code from an image file and returns the decoded data.

    Args:
        image_path (str): The path to the QR code image.

    Returns:
        str: The decoded data from the QR code.
    """
    try:
        from pyzbar.pyzbar import decode
        from PIL import Image
        decoded_objects = decode(Image.open(image_path))
        if decoded_objects:
            return decoded_objects[0].data.decode('utf-8')
        else:
            return "No QR code found."
    except Exception as e:
        raise ValueError(f"QR code reading error: {e}")