from itertools import chain
from typing import Union, Optional
import discord

class _BaseDisplay:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)

    def has(self, name):
        return True if getattr(self, name, None) else False

    @property
    def keys(self) -> tuple:
        return tuple(self.kwargs.keys())

    @property
    def _attr_to_list(self) -> list:
        return list(self.kwargs.values())

    @property
    def _attr_to_list_filtered(self):
        return filter(lambda x: True if x else False, self._attr_to_list)

    @property
    def to_kwargs(self):
        return dict(filter(lambda val: bool(val[1]), self.kwargs.items()))

    @property
    def to_args(self):
        return self._attr_to_list

    def set_args(self, *args):
        r = []
        o = self._attr_to_list
        for i in range(len(args)):
            if o[i]:
                r.append(o[i])
            else:
                r.append(args[i])
        return r

    def set_kwargs(self, **kwargs):
        for k, v in kwargs.items():
            self.kwargs[k] = v
            setattr(self, k, v)
        return kwargs

    @classmethod
    def from_args(cls, *args):
        return cls.__new__(cls).__init__(**cls.args_to_kwargs(*args))

    @staticmethod
    def args_to_kwargs(*args):
        return {arg: arg for arg in args}

class ButtonDisplay(_BaseDisplay):
    def __init__(self, label: Union[str] = None, emoji: Union[str] = None, color: Union[discord.ButtonStyle] = None):
        super().__init__(label=label, emoji=emoji, color=color)

    @property
    def _attr_name_to_list(self):
        return self._attr_to_list[:-1]

    @property
    def _attr_name_to_list_filtered(self):
        return filter(lambda x: True if x else False, self._attr_name_to_list)

    @property
    def ButtonContent(self):
        return "".join(self._attr_name_to_list_filtered)

class DropdownDisplay(_BaseDisplay):
    def __init__(self, emoji: Optional[str] = None, label: Optional[str] = None, description: Optional[str] = None, color: Optional[discord.ButtonStyle] = None):
        super().__init__(emoji=emoji, label=label,  description=description, color=color)

class SelectOptionDisplay(_BaseDisplay):
    def __init__(self, emoji: Optional[str] = None, label: Optional[str] = None, description: Optional[str] = None):
        super().__init__(emoji=emoji, label=label, description=description)