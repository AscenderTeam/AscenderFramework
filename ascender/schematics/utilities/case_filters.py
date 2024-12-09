import re


def pascal_case(word: str):
    """Converts a string into PascalCase."""
    word = re.sub(r'[-_]', ' ', word)
    word = ''.join(part.capitalize() for part in word.split())
    
    return word

def snake_case(word: str) -> str:
    """Converts a string into snake_case."""
    word = re.sub(r'[-\s]', '_', word)  # Replace hyphens and spaces with underscores
    word = word.lower()  # Convert to lowercase
    return word

def kebab_case(word: str) -> str:
    """Converts a string into kebab-case."""
    word = re.sub(r'[_\s]', '-', word)  # Replace underscores and spaces with hyphens
    word = word.lower()  # Convert to lowercase
    return word