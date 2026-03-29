# -*- coding: utf-8 -*-
"""Tests for UTF-8 utilities module."""

import unittest
import tempfile
import os
from src.utf8_utils import (
    is_valid_utf8,
    detect_character_type,
    validate_utf8_file,
    sanitize_utf8,
    get_string_info,
)


class TestChineseCharacters(unittest.TestCase):
    """Test Chinese character handling (中文测试)."""

    def test_simplified_chinese_encoding(self):
        """Test encoding/decoding of simplified Chinese characters."""
        text = "中文测试"
        encoded = text.encode('utf-8')
        decoded = encoded.decode('utf-8')
        self.assertEqual(text, decoded)

    def test_traditional_chinese(self):
        """Test traditional Chinese characters."""
        text = "繁體字測試"
        self.assertTrue(is_valid_utf8(text))

    def test_chinese_string_info(self):
        """Test string info for Chinese text."""
        info = get_string_info("中文测试")
        self.assertEqual(info['char_count'], 4)
        self.assertIn('cjk', info['character_types'])

    def test_detect_chinese_characters(self):
        """Test detection of Chinese characters."""
        char_type = detect_character_type('中')
        self.assertEqual(char_type, 'cjk')

    def test_mixed_chinese_english(self):
        """Test mixed Chinese and English text."""
        text = "Hello 世界 World"
        self.assertTrue(is_valid_utf8(text))
        info = get_string_info(text)
        self.assertIn('ascii', info['character_types'])
        self.assertIn('cjk', info['character_types'])


class TestJapaneseCharacters(unittest.TestCase):
    """Test Japanese character handling (日本語)."""

    def test_hiragana(self):
        """Test Hiragana characters."""
        text = "ひらがな"
        self.assertTrue(is_valid_utf8(text))

    def test_katakana(self):
        """Test Katakana characters."""
        text = "カタカナ"
        self.assertTrue(is_valid_utf8(text))

    def test_kanji(self):
        """Test Kanji characters."""
        text = "日本語漢字"
        self.assertTrue(is_valid_utf8(text))

    def test_mixed_japanese(self):
        """Test mixed Japanese writing systems."""
        text = "日本語のテストです"
        info = get_string_info(text)
        self.assertIn('cjk', info['character_types'])

    def test_detect_japanese_characters(self):
        """Test detection of Japanese characters."""
        self.assertEqual(detect_character_type('あ'), 'hiragana')
        self.assertEqual(detect_character_type('ア'), 'katakana')
        self.assertEqual(detect_character_type('日'), 'cjk')


class TestEmojis(unittest.TestCase):
    """Test emoji handling (émojis)."""

    def test_single_emoji(self):
        """Test single emoji character."""
        text = "😀"
        self.assertTrue(is_valid_utf8(text))
        self.assertEqual(detect_character_type('😀'), 'emoji')

    def test_emoji_sequence(self):
        """Test emoji sequences with skin tone modifiers."""
        text = "👍🏽"
        self.assertTrue(is_valid_utf8(text))

    def test_zwj_emoji_sequence(self):
        """Test zero-width joiner emoji sequences."""
        text = "👨‍👩‍👧‍👦"
        self.assertTrue(is_valid_utf8(text))

    def test_mixed_emoji_text(self):
        """Test mixed emoji and text."""
        text = "Hello 😀 世界 🌍"
        info = get_string_info(text)
        self.assertIn('emoji', info['character_types'])
        self.assertIn('cjk', info['character_types'])
        self.assertIn('ascii', info['character_types'])

    def test_multiple_emojis(self):
        """Test multiple emoji characters."""
        text = "🎉🎊🎈🎁"
        self.assertTrue(is_valid_utf8(text))


class TestEdgeCases(unittest.TestCase):
    """Test edge cases in UTF-8 handling."""

    def test_empty_string(self):
        """Test empty string handling."""
        self.assertTrue(is_valid_utf8(""))
        info = get_string_info("")
        self.assertEqual(info['char_count'], 0)

    def test_ascii_only(self):
        """Test ASCII-only text."""
        text = "Hello World"
        self.assertTrue(is_valid_utf8(text))
        self.assertEqual(detect_character_type('H'), 'ascii')

    def test_mixed_multibyte_singlebyte(self):
        """Test mixed multi-byte and single-byte characters."""
        text = "A中B日C文D"
        self.assertTrue(is_valid_utf8(text))
        info = get_string_info(text)
        self.assertEqual(info['char_count'], 7)

    def test_bom_handling(self):
        """Test BOM (Byte Order Mark) handling."""
        text_with_bom = '\ufeffHello'
        self.assertTrue(is_valid_utf8(text_with_bom))

    def test_invalid_utf8_sequence(self):
        """Test detection of invalid UTF-8 sequences."""
        invalid_bytes = b'\xff\xfe'
        result = is_valid_utf8(invalid_bytes)
        self.assertFalse(result)

    def test_sanitize_invalid_utf8(self):
        """Test sanitization of invalid UTF-8."""
        invalid_bytes = b'Hello \xff\xfe World'
        sanitized = sanitize_utf8(invalid_bytes)
        self.assertTrue(is_valid_utf8(sanitized))

    def test_very_long_mixed_string(self):
        """Test very long strings with mixed encodings."""
        parts = ["English ", "中文 ", "日本語 ", "😀 ", "Español "]
        text = "".join(parts * 1000)
        self.assertTrue(is_valid_utf8(text))
        info = get_string_info(text)
        self.assertGreater(info['char_count'], 5000)


class TestFileOperations(unittest.TestCase):
    """Test file-based UTF-8 operations."""

    def test_write_read_utf8_file(self):
        """Test writing and reading UTF-8 content to file."""
        content = "中文测试 日本語 😀 Hello"
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as f:
            f.write(content)
            temp_path = f.name

        try:
            with open(temp_path, 'r', encoding='utf-8') as f:
                read_content = f.read()
            self.assertEqual(content, read_content)
            self.assertTrue(validate_utf8_file(temp_path))
        finally:
            os.unlink(temp_path)

    def test_validate_utf8_file_valid(self):
        """Test validation of valid UTF-8 file."""
        content = "Valid UTF-8: 中文 日本 🎉"
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as f:
            f.write(content)
            temp_path = f.name

        try:
            self.assertTrue(validate_utf8_file(temp_path))
        finally:
            os.unlink(temp_path)

    def test_chinese_filename(self):
        """Test file operations with Chinese filename."""
        content = "测试内容"
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "中文文件名.txt")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            with open(filepath, 'r', encoding='utf-8') as f:
                read_content = f.read()
            self.assertEqual(content, read_content)


class TestStringInfo(unittest.TestCase):
    """Test string information extraction."""

    def test_character_count(self):
        """Test accurate character counting."""
        # Emoji with skin tone modifier should count as multiple code points
        text = "👨‍👩‍👧‍👦"  # Family emoji (ZWJ sequence)
        info = get_string_info(text)
        self.assertGreater(info['codepoint_count'], 1)

    def test_byte_count(self):
        """Test byte count calculation."""
        text = "中文"
        info = get_string_info(text)
        # Each Chinese character is 3 bytes in UTF-8
        self.assertEqual(info['byte_count'], 6)

    def test_character_types_identification(self):
        """Test identification of all character types."""
        text = "A中あア😀"
        info = get_string_info(text)
        self.assertIn('ascii', info['character_types'])
        self.assertIn('cjk', info['character_types'])
        self.assertIn('hiragana', info['character_types'])
        self.assertIn('katakana', info['character_types'])
        self.assertIn('emoji', info['character_types'])


if __name__ == '__main__':
    unittest.main()
