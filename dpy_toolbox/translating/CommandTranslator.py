from typing import Any
import discord
from discord import app_commands
from discord.ext import commands
from ..core.default import get_multiattr

__all__ = (
    "CommandTranslator",
    "translate_command",
    "default_language",
    "translate_polyglot",
    "translate_params_description",
    "translate_params_name",
    "translate_command_description"
)

class CommandTranslator(app_commands.Translator):
    RELEVANT = {
        "TranslationContextLocation.command_name": "__translating",
        "TranslationContextLocation.command_description": "__translating_desc",
        "TranslationContextLocation.parameter_name": "_Parameter__parent.__translating_name",
        "TranslationContextLocation.parameter_description":  "_Parameter__parent.__translating_desc"
    }

    def __init__(self, default=None):
        self.default = default
        super().__init__()

    def get_default(self, ctx):
        if isinstance(ctx.data, app_commands.Parameter):
            return getattr(ctx.data._Parameter__parent, "__translating_default", None)
        else:
            return getattr(ctx.data, "__translating_default", None)

    # string: what to translate (might be arg, command, description, ...)
    # locale: the string of the local (in the language that should be translated)
    # context: discord.app_commands.translator.TranslationContext
    async def translate(self, string: str, locale: str, context):
        s = str(string)
        search_for_param = self.RELEVANT.get(str(context.location), "")
        default = self.get_default(context) or self.default
        trans_to_lang = locale[1]
        translation = get_multiattr(context.data, *search_for_param.split("."), default={})
        if not translation:
            return translation.get(default, s)
        for lang, trans in translation.items():
            if trans_to_lang.startswith(lang):
                return trans
        return translation.get(default, s)


def default_language(lang: str) -> Any:
    def decorator(command: commands.Command):
        command.__translating_default = lang
        for param in command._params.values():
            param.__translating_default = lang
        return command
    return decorator


def translate_params_description(lang, **kwargs: str) -> Any:
    def decorator(command: commands.Command):
        for k, v in kwargs.items():
            parameter = command._params.get(k, None)
            if not parameter:
                continue
            if getattr(parameter, "__translating_desc", None) is None:
                parameter.__translating_desc = {}
            parameter.__translating_desc[lang] = v
            command._params[k] = parameter
        return command
    return decorator


def translate_params_name(lang, **kwargs: str) -> Any:
    def decorator(command: commands.Command):
        for k, v in kwargs.items():
            parameter = command._params.get(k, None)
            if not parameter:
                continue
            if getattr(parameter, "__translating_name", None) is None:
                parameter.__translating_name = {}
            parameter.__translating_name[lang] = v
            command._params[k] = parameter
        return command
    return decorator


def translate_command(lang, name) -> Any:
    def decorator(command: commands.Command):
        if getattr(command, '__translating', None) is None:
            command.__translating = {}
        command.__translating[lang] = name
        return command
    return decorator


def translate_command_description(lang, *description: str) -> Any:
    def decorator(command: commands.Command):
        if getattr(command, '__translating_desc', None) is None:
            command.__translating_desc = {}
        command.__translating_desc[lang] = " ".join(description)
        return command
    return decorator


def translate_polyglot(**kwargs) -> Any:
    def decorator(command: commands.Command):
        if getattr(command, '__translating', None) is None:
            command.__translating = {}
        for k, v in kwargs.items():
            command.__translating[k] = v
        return command
    return decorator
