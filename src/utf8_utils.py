# -*- coding: utf-8 -*-
"""
UTF-8 Utilities Module

Provides utilities for handling UTF-8 encoding with support for:
- Chinese characters (中文测试)
- Japanese characters (日本語)
- Emojis (émojis)
- Edge cases and validation
"""

import os
import re
import unicodedata
from typing import Dict, List, Set, Union


def is_valid_utf8(data: Union[str, bytes]) -> bool:
    """
    Check if the given data is valid UTF-8.

    Args:
        data: String or bytes to validate.

    Returns:
        True if valid UTF-8, False otherwise.
    """
    if isinstance(data, str):
        return True  # Python strings are already validated
    if isinstance(data, bytes):
        try:
            data.decode('utf-8')
            return True
        except UnicodeDecodeError:
            return False
    return False


def detect_character_type(char: str) -> str:
    """
    Detect the type of a single character.

    Args:
        char: A single character string.

    Returns:
        Character type: 'ascii', 'cjk', 'hiragana', 'katakana', 'emoji', or 'other'.
    """
    if len(char) == 0:
        return 'other'

    code_point = ord(char[0])

    # ASCII range
    if code_point < 128:
        return 'ascii'

    # Check for emoji first (various ranges)
    if is_emoji(char):
        return 'emoji'

    # Hiragana: U+3040 to U+309F
    if 0x3040 <= code_point <= 0x309F:
        return 'hiragana'

    # Katakana: U+30A0 to U+30FF
    if 0x30A0 <= code_point <= 0x30FF:
        return 'katakana'

    # CJK Unified Ideographs and Extensions
    if (
        (0x4E00 <= code_point <= 0x9FFF) or  # CJK Unified Ideographs
        (0x3400 <= code_point <= 0x4DBF) or  # CJK Extension A
        (0x20000 <= code_point <= 0x2A6DF) or  # CJK Extension B
        (0x2A700 <= code_point <= 0x2B73F) or  # CJK Extension C
        (0x2B740 <= code_point <= 0x2B81F) or  # CJK Extension D
        (0x2B820 <= code_point <= 0x2CEAF)     # CJK Extension E
    ):
        return 'cjk'

    return 'other'


def is_emoji(char: str) -> bool:
    """
    Check if a character is an emoji.

    Args:
        char: A character or string to check.

    Returns:
        True if the character is an emoji.
    """
    if len(char) == 0:
        return False

    # Common emoji ranges
    emoji_ranges = [
        (0x1F600, 0x1F64F),  # Emoticons
        (0x1F300, 0x1F5FF),  # Misc Symbols and Pictographs
        (0x1F680, 0x1F6FF),  # Transport and Map
        (0x1F1E0, 0x1F1FF),  # Flags
        (0x2600, 0x26FF),    # Misc symbols
        (0x2700, 0x27BF),    # Dingbats
        (0xFE00, 0xFE0F),    # Variation Selectors
        (0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
        (0x1FA00, 0x1FA6F),  # Chess Symbols
        (0x1FA70, 0x1FAFF),  # Symbols and Pictographs Extended-A
        (0x231A, 0x231B),    # Watch, Hourglass
        (0x23E9, 0x23F3),    # Various
        (0x23F8, 0x23FA),    # Various
        (0x25AA, 0x25AB),    # Squares
        (0x25B6, 0x25B6),    # Play button
        (0x25C0, 0x25C0),    # Reverse button
        (0x25FB, 0x25FE),    # Squares
        (0x2614, 0x2615),    # Umbrella, Hot Beverage
        (0x2648, 0x2653),    # Zodiac
        (0x267F, 0x267F),    # Wheelchair
        (0x2693, 0x2693),    # Anchor
        (0x26A1, 0x26A1),    # High Voltage
        (0x26AA, 0x26AB),    # Circles
        (0x26BD, 0x26BE),    # Sports
        (0x26C4, 0x26C5),    # Snowman, Sun
        (0x26CE, 0x26CE),    # Ophiuchus
        (0x26D4, 0x26D4),    # No entry
        (0x26EA, 0x26EA),    # Church
        (0x26F2, 0x26F3),    # Fountain, Golf
        (0x26F5, 0x26F5),    # Sailboat
        (0x26FA, 0x26FA),    # Tent
        (0x26FD, 0x26FD),    # Fuel pump
        (0x2702, 0x2702),    # Scissors
        (0x2705, 0x2705),    # Check mark
        (0x2708, 0x270D),    # Various
        (0x270F, 0x270F),    # Pencil
        (0x2712, 0x2712),    # Black Nib
        (0x2714, 0x2714),    # Check mark
        (0x2716, 0x2716),    # X mark
        (0x271D, 0x271D),    # Cross
        (0x2721, 0x2721),    # Star of David
        (0x2728, 0x2728),    # Sparkles
        (0x2733, 0x2734),    # Eight-pointed star
        (0x2744, 0x2744),    # Snowflake
        (0x2747, 0x2747),    # Sparkle
        (0x274C, 0x274C),    # Cross mark
        (0x274E, 0x274E),    # Cross mark
        (0x2753, 0x2755),    # Question marks
        (0x2757, 0x2757),    # Exclamation mark
        (0x2763, 0x2764),    # Heart exclamation, Heart
        (0x2795, 0x2797),    # Math symbols
        (0x27A1, 0x27A1),    # Right arrow
        (0x27B0, 0x27B0),    # Curly loop
        (0x27BF, 0x27BF),    # Double curly loop
        (0x2934, 0x2935),    # Arrows
        (0x2B05, 0x2B07),    # Arrows
        (0x2B1B, 0x2B1C),    # Squares
        (0x2B50, 0x2B50),    # Star
        (0x2B55, 0x2B55),    # Circle
        (0x3030, 0x3030),    # Wavy dash
        (0x303D, 0x303D),    # Part alternation mark
        (0x3297, 0x3297),    # Circled ideograph congratulation
        (0x3299, 0x3299),    # Circled ideograph secret
    ]

    code_point = ord(char[0])

    for start, end in emoji_ranges:
        if start <= code_point <= end:
            return True

    # Check for emoji using unicode name
    try:
        name = unicodedata.name(char[0], '')
        if 'EMOJI' in name or 'FACE' in name:
            return True
    except ValueError:
        pass

    return False


def validate_utf8_file(filepath: str) -> bool:
    """
    Validate that a file contains valid UTF-8 encoded content.

    Args:
        filepath: Path to the file to validate.

    Returns:
        True if file is valid UTF-8, False otherwise.
    """
    if not os.path.exists(filepath):
        return False

    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        content.decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False
    except IOError:
        return False


def sanitize_utf8(data: Union[str, bytes], replacement: str = '') -> str:
    """
    Sanitize data to ensure valid UTF-8 output.

    Args:
        data: Input string or bytes.
        replacement: Character to use for invalid sequences.

    Returns:
        Valid UTF-8 string.
    """
    if isinstance(data, str):
        return data

    if isinstance(data, bytes):
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            # Decode with error handling
            return data.decode('utf-8', errors='replace')

    return str(data)


def get_string_info(text: str) -> Dict:
    """
    Get detailed information about a UTF-8 string.

    Args:
        text: Input string to analyze.

    Returns:
        Dictionary with string information including:
        - char_count: Number of characters (grapheme clusters approximation)
        - codepoint_count: Number of Unicode code points
        - byte_count: Number of bytes in UTF-8 encoding
        - character_types: Set of character types present
    """
    info = {
        'char_count': len(text),
        'codepoint_count': len(text),
        'byte_count': len(text.encode('utf-8')),
        'character_types': set()
    }

    for char in text:
        char_type = detect_character_type(char)
        info['character_types'].add(char_type)

    return info


def encode_utf8(text: str) -> bytes:
    """
    Encode a string to UTF-8 bytes.

    Args:
        text: Input string.

    Returns:
        UTF-8 encoded bytes.
    """
    return text.encode('utf-8')


def decode_utf8(data: bytes) -> str:
    """
    Decode UTF-8 bytes to string.

    Args:
        data: UTF-8 encoded bytes.

    Returns:
        Decoded string.

    Raises:
        UnicodeDecodeError: If data is not valid UTF-8.
    """
    return data.decode('utf-8')


def contains_cjk(text: str) -> bool:
    """
    Check if text contains any CJK characters.

    Args:
        text: Input string.

    Returns:
        True if CJK characters are present.
    """
    for char in text:
        if detect_character_type(char) == 'cjk':
            return True
    return False


def contains_emoji(text: str) -> bool:
    """
    Check if text contains any emoji characters.

    Args:
        text: Input string.

    Returns:
        True if emoji characters are present.
    """
    for char in text:
        if is_emoji(char):
            return True
    return False


def normalize_utf8(text: str, form: str = 'NFC') -> str:
    """
    Normalize a UTF-8 string to a canonical form.

    Args:
        text: Input string.
        form: Normalization form (NFC, NFD, NFKC, NFKD).

    Returns:
        Normalized string.
    """
    return unicodedata.normalize(form, text)
