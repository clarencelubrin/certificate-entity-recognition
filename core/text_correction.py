import re

def regex_pipeline(text):
    """
    Cleans text using a series of regex rules.
    """
    # Removes '(' or '{' at the start of a word
    text = re.sub(r'[\(\{\[](\b\w)', r'\1', text) 
    # Removes ')' or '}' or ':' or '.' at the end of a word (if not a proper end)
    text = re.sub(r'(\w\b)[\)\}\]\:]', r'\1', text)
    # Handle specific cases like 2020)-2022
    text = re.sub(r'(\d)\)-(\d)', r'\1-\2', text)
    
    # Remove any '(' that is not followed by a word character (i.e., stray before space/punct)
    text = re.sub(r'\((?!\w)', '', text)
    # Remove any opening bracket that is isolated (surrounded by space or string boundaries)
    text = re.sub(r'(?<=\s)[\(\[\{]+(?=\s)', '', text)
    # Remove opening brackets at start/end adjacent to non-word characters or string boundaries
    text = re.sub(r'^[\(\[\{]+', '', text)
    text = re.sub(r'[\(\[\{]+$', '', text)
    # Collapse multiple spaces introduced by removals
    text = re.sub(r'\s{2,}', ' ', text).strip()

    # Remove runs of random punctuation (e.g. "'}$") and isolated stray symbols
    text = re.sub(r'[^\w\s]{2,}', ' ', text)                                 # long runs of non-word chars
    text = re.sub(r'(?<=\s)[^\w\s](?=\s)', '', text)                          # single stray symbol between spaces
    text = re.sub(r'(?<=\w)[^\w\s\'\-\.\,]+(?=\s)', '', text)                     # punctuation after a word (keep apostrophe/hyphen)
    text = re.sub(r'(?<=\s)[^\w\s\'\-\.\,]+(?=\w)', '', text)                     # punctuation before a word (keep apostrophe/hyphen)
    # Remove leftover isolated braces/angle brackets/quotes
    text = re.sub(r'[\{\}\[\]\<\>\"“”`´]', '', text)
    # Final collapse of multiple spaces
    text = re.sub(r'\s{2,}', ' ', text).strip()
    # Remove runs of '=' and isolated '=' between tokens (common OCR artifacts)
    text = re.sub(r'=+', ' ', text)
    text = re.sub(r'(?<=\S)\s*=\s*(?=\S)', ' ', text)
    # Trim any leading/trailing '=' that may remain
    text = re.sub(r'^=+|=+$', '', text)
    # Collapse multiple spaces introduced by removals
    text = re.sub(r'\s{2,}', ' ', text).strip()
    
    # Look for a slash/underscore optionally surrounded by spaces.
    text = re.sub(r'(?<!\d)\s*[\/_]\s*(?!\d)', ' ', text)

    # Fixes "DrWinifel" -> "Dr Winifel"
    text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)

    # 3. FIX RUN-TOGETHER INITIALS (The "LBarbierra" Fix)
    # Fixes "LBarbierra" -> "L Barbierra" or "J.Cruz" -> "J. Cruz"
    text = re.sub(r'\b([A-Z]\.?)([A-Z][a-z]+)', r'\1 \2', text)

    # Remove double spaces created by the replacements above
    text = re.sub(r'\s+', ' ', text).strip()

    # Remove ' that is not in a contraction or possessive form
    text = re.sub(r"(?<!\w)'(?!\w)", '', text)
    # Remove " that has no word characters around it
    text = re.sub(r'(?<=\s)"(?=\s)', '', text)
    # Remove " that is at the start or end of the text
    text = re.sub(r'^"|"$', '', text)
    # Remove " that are no ending quotes (i.e., not followed by space or punctuation)
    text = re.sub(r'"(?=\S)', '', text)

    return text
