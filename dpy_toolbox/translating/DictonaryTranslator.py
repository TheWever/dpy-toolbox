from typing import Any
from discord import app_commands
from discord.ext import commands
from ..core.default import get_multikey_dict_item

__all__ = (
    "DictonaryTranslator",
)

class DictonaryTranslator(app_commands.Translator):
    """
    A Translator that will translate the command using the provided translation table

    """
    RELEVANT = {
        "TranslationContextLocation.command_name": lambda ctx: "name",
        "TranslationContextLocation.command_description": lambda ctx: "description",
        "TranslationContextLocation.parameter_name": lambda ctx: f"params.{ctx.name}.name",
        "TranslationContextLocation.parameter_description": lambda ctx: f"params.{ctx.name}.description",
    }

    def __init__(self, translation_table, default=None):
        self.translator = translation_table
        self.default = default
        super().__init__()

    def get_default(self, command_table, search_strings):
        var = command_table.get(command_table.get("default"), None)
        return get_multikey_dict_item(var, *search_strings, default=None) if var else None

    # string: what to translate (might be arg, command, description, ...)
    # locale: the string of the local (in the language that should be translated)
    # context: discord.app_commands.translator.TranslationContext
    async def translate(self, string: str, locale: str, context):
        s = str(string)
        search_for_param = self.RELEVANT.get(str(context.location), "")(context.data).split(".")
        trans_to_lang = locale[1]
        translator = None
        command_name = context.data.name if isinstance(context.data, (app_commands.Command)) else context.data.command.name
        cmd_tab = self.translator.get(command_name, None)
        if not cmd_tab:
            return s
        for lang, trans in cmd_tab.items():
            if trans_to_lang.startswith(lang):
                translator = trans
        if not translator:
            return self.get_default(cmd_tab, search_for_param) or s
        translation = get_multikey_dict_item(translator, *search_for_param, default={})
        return translation or s
