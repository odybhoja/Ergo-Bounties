import re

def check_bounty_labels(labels):
    """
    Check if any label contains 'bounty' or 'b-'.
    
    Args:
        labels (list): List of label objects
        
    Returns:
        bool: True if any label contains 'bounty' or 'b-'
    """
    return any("bounty" in label['name'].lower() or "b-" in label['name'].lower() for label in labels)

def extract_bounty_from_labels(labels):
    """
    Extract bounty amount and currency from issue labels.
    
    Args:
        labels (list): List of label objects
        
    Returns:
        tuple: (amount, currency) or (None, None) if not found
    """
    label_patterns = [
        # Cryptocurrency patterns
        r'bounty\s*-?\s*(\d+)\s*(sigusd|rsn|bene|erg|gort)',
        r'b-(\d+)\s*(sigusd|rsn|bene|erg|gort)',
        r'(\d+)\s*(sigusd|rsn|bene|erg|gort)\s*bounty',
        # Precious metals patterns
        r'bounty\s*-?\s*(\d+(?:\.\d+)?)\s*(gram|g|oz|ounce)s?\s+(?:of\s+)?(gold|silver|platinum)',
        r'(\d+(?:\.\d+)?)\s*(gram|g|oz|ounce)s?\s+(?:of\s+)?(gold|silver|platinum)\s*bounty'
    ]
    
    for label in labels:
        label_name = label['name'].lower()
        for pattern in label_patterns:
            match = re.search(pattern, label_name, re.IGNORECASE)
            if match:
                if match.groups()[-1] in ['gold', 'silver', 'platinum']:
                    amount = match.group(1)
                    unit = match.group(2).lower()
                    metal = match.group(3).upper()
                    
                    unit = {
                        'gram': 'g',
                        'g': 'g',
                        'oz': 'oz',
                        'ounce': 'oz'
                    }.get(unit, unit)
                    
                    return amount, f"{unit} {metal}"
                else:
                    amount = match.group(1)
                    currency = match.group(2).upper()
                    if currency == 'SIGUSD':
                        currency = 'SigUSD'
                    return amount, currency
    return None, None

def extract_bounty_from_text(title, body):
    """
    Extract bounty amount and currency from issue title and body.
    
    Args:
        title (str): Issue title
        body (str): Issue body
        
    Returns:
        tuple: (amount, currency) or (None, None) if not found
    """
    patterns = [
        r'bounty:?\s*[\$€£]?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(sigusd|gort|rsn|bene|erg|usd|ergos?|dollars?|€|£|\$)?',
        r'[\$€£]\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:sigusd|gort|rsn|bene|erg|usd|ergos?|bounty)',
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(sigusd|gort|rsn|bene|erg|usd|ergos?)\s*bounty',
        r'bounty:?\s*(\d+(?:\.\d+)?)\s*(gram|g|oz|ounce)s?\s+(?:of\s+)?(gold|silver|platinum)',
        r'(\d+(?:\.\d+)?)\s*(gram|g|oz|ounce)s?\s+(?:of\s+)?(gold|silver|platinum)\s*bounty'
    ]
    
    text = f"{title} {body}".lower()
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(match.groups()) == 3 and match.group(3) in ['gold', 'silver', 'platinum']:
                amount = match.group(1)
                unit = match.group(2).lower()
                metal = match.group(3).upper()
                
                unit = {
                    'gram': 'g',
                    'g': 'g',
                    'oz': 'oz',
                    'ounce': 'oz'
                }.get(unit, unit)
                
                return amount, f"{unit} {metal}"
            else:
                amount = match.group(1).replace(',', '')
                currency = match.group(2) if len(match.groups()) > 1 and match.group(2) else 'USD'
                
                currency = {
                    '$': 'USD',
                    '€': 'EUR',
                    '£': 'GBP',
                    'dollars': 'USD',
                    'erg': 'ERG',
                    'ergos': 'ERG',
                    'sigusd': 'SigUSD',
                    'rsn': 'RSN',
                    'bene': 'BENE',
                    'gort': 'GORT'
                }.get(currency.lower(), currency.upper())
                
                return amount, currency
    
    return None, None
