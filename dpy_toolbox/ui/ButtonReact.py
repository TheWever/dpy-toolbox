import discord
from dpy_toolbox.ui.core import ButtonDisplay
from typing import Union, Callable

class ButtonReact(discord.ui.View):
    def __init__(self, timeout: Union[int] = 120):
        self._timeout = timeout

        super().__init__(timeout=self._timeout)

    def _template(self, f):
        async def wrapped(interaction: discord.Interaction):
            await f(interaction)

        return wrapped

    def add(self, callback: Union[Callable], btn: Union[ButtonDisplay]):
        """
        Add a button to the table and attach a callback func
        :param callback: The function that will be called upon reaction add and remove
        :param ButtonDisplay btn: The display of the buttom
        """
        f = discord.ui.Button(**btn.to_kwargs)
        f.callback = self._template(callback)

        self.add_item(f)

    def remove(self, index: Union[int]):
        """
        Remove item by index from table
        :param index: Index of the item
        """
        self.remove_item(self.children[index])

class ButtonReactRoler(ButtonReact):
    def _template(self, roles, rm=True):
        async def wrapped(interaction: discord.Interaction):
            if rm and all(x in interaction.user.roles for x in roles):
                await interaction.user.remove_roles(*roles)
            else:
                await interaction.user.add_roles(*roles)
            await interaction.response.defer()

        return wrapped

    async def add(self, role: Union[discord.Role, list[discord.Role]], btn: Union[ButtonDisplay], remove_role: Union[bool] = True):
        """
        Add a btn to the table and attach a callback func
        :param discord.Role role: The role you want to add and remove
        :param ButtonDisplay btn: The look of the button
        """
        f = discord.ui.Button(**btn.to_kwargs)
        f.callback = self._template(
            [role] if isinstance(role, discord.Role) else role,
            remove_role
        )
        self.add_item(f)

    def remove(self, index: Union[int]):
        """
        Remove item by index from table
        :param index: Index of the item
        """
        self.remove_item(self.children[index])