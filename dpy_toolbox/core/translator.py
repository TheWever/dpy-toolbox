from typing import Any
from .default import MISSING
import discord
from discord import app_commands

class _BaseTranslator:
    DEFAULT_TRANSLATOR = {}
    DEFAULT_TYPES = {}

    def __init__(self, translator: dict = None, allowed: list[Any, Any] = None):
        self.__translation_table = translator or self.DEFAULT_TRANSLATOR or {}
        self.__allowed_types = allowed or self.DEFAULT_TYPES or [Any, Any]

    def set_key_type(self, dtype: Any):
        self.__allowed_types[0] = dtype

    def set_value_type(self, dtype: Any):
        self.__allowed_types[1] = dtype

    def add_translation(self, key: Any, value: Any):
        for i, x in (key, value):
            if not isinstance(x, self.__allowed_types[i]):
                raise IndexError(f"{key} is not a valid key!")
        if key in self.__translation_table:
            raise ValueError(f"{key} is already registered in translation table!")
        self.__translation_table[key] = value

    def delete_translation(self, key: Any):
        if key not in self.__translation_table:
            raise IndexError(f"{key} is not part of translation table!")
        self.__translation_table.pop(key)

    def translate(self, key: Any, default: Any = MISSING):
        if isinstance(default, MISSING):
            return self.__translation_table.get(key)

        return self.__translation_table.get(key, default)

    def get(self, key: Any, default: Any = MISSING):
        return self.translate(key, default)

    def __call__(self, *args, **kwargs):
        self.translate(*args, **kwargs)


class AutoHelpTranslator(_BaseTranslator):
    DEFAULT_TRANSLATOR = {
        "not_found": " [any] ",
        "required": " [required] ",
        "not_required": " [not required] ",
        str: " [text]",
        discord.AppCommandOptionType.string: " [text] ",
        int: " [number]",
        discord.AppCommandOptionType.integer: " [number] ",
        discord.Member: " [user] ",
        discord.TextChannel: " [text channel] ",
        discord.VoiceChannel: " [voice channel] ",
        discord.CategoryChannel: " [category] ",
        discord.Role: " [role] "
    }

    DEFAULT_TYPES = [
        Any, str
    ]
