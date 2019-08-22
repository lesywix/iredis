"""
Render redis-server responses.
This module will be auto loaded to callbacks.

func(redis-response, completers: GrammarCompleter) -> formatted result(str)
"""
import re
import logging
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import to_formatted_text, FormattedText

from .style import STYLE_DICT
from .config import config

logger = logging.getLogger(__name__)


def _literal_bytes(b):
    """
    convert bytes to printable text.

    backslash and double-quotes will be escaped by
    backslash.
    "hello\" -> \"hello\\\"

    we don't add outter double quotes here, since
    completer also need this function's return value
    to patch completers.
    
    b'hello' -> "hello"
    b'double"quotes"' -> "double\"quotes\""
    """
    s = str(b)
    s = s[2:-1]  # remove b' '
    # unescape single quote
    s = s.replace(r"\'", "'")
    return s


def render_simple_strings(text, style=None):
    if isinstance(text, bytes):
        text = output_bytes(text)
    text = f'"{text}"'
    return FormattedText([("", text)])


def render_int(value, completers=None):
    return value


def render_list(byte_items, str_items, style=None):
    if config.raw:
        return b"\n".join(byte_items)
    index_width = len(str(len(str_items)))
    rendered = []
    for index, item in enumerate(str_items):
        index_const_width = f"{index+1:{index_width}})"
        rendered.append(("", index_const_width))
        if index + 1 < len(str_items):
            text = f" {item}\n"
        else:  # last one don't have \n
            text = f" {item}"
        rendered.append((style, text))
    return FormattedText(rendered)


def render_ok(text, completer):
    """
    If response is b'OK', render ok with success color.
    else render message with Error color.
    """
    text = _ensure_str(text)
    if text == "OK":
        return FormattedText([(STYLE_DICT["success"], text)])
    return FormattedText([(STYLE_DICT["error"], text)])


def command_keys(items, completer):
    str_items = _ensure_str(items)

    # update completers
    if completer:
        completer.completers["key"] = WordCompleter(str_items)
        completer.completers["keys"] = WordCompleter(str_items)
        logger.debug(f"[Completer] key completer updated.")
    else:
        logger.debug(f"[Completer] completer is None, not updated.")

    # render is render, completer is completer
    # render and completer are in same function but code are splitted.
    # Give back to Ceasar what is Ceasar's and to God what is God's.
    double_quoted = _double_quotes(str_items)
    rendered = render_list(items, double_quoted, STYLE_DICT["key"])
    return rendered
