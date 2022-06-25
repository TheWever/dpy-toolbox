from typing import Union, Iterable, Optional
import discord
from itertools import chain
from ..ui.core import ButtonDisplay, DropdownDisplay, SelectOptionDisplay

class Page:
    def __init__(self, content: Union[str, discord.Embed]):
        """
        A page of a book
        :param content: The page content
        """
        self.content = content

class SelectPage:
    def __init__(self, content: Union[str, discord.Embed], label: Union[str] = None, description: Union[str] = None, emoji: Union[str] = None, buttons: Union[discord.Button, list[discord.Button], None] = None):
        """
        A page that
        :param content: The message that will be displayed
        :param label: The name of the option
        :param description: The description of the option
        :param emoji: The emoji that is apart of the label
        :param buttons: All buttons the page will display
        """
        self.content = content
        self.buttons = []
        if buttons:
            self.buttons = [buttons] if not isinstance(buttons, Iterable) else buttons
        self.label = label
        self.description = description
        self.emoji = emoji

    @property
    def to_args(self):
        return self.label, self.description, self.emoji

    @property
    def to_kwargs(self):
        return {"label": self.label, "description": self.description, "emoji": self.emoji}

class Book:
    """
    A collection of pages
    """
    def __init__(self, iterator: Union[Iterable]):
        self._iterator = iterator

    @property
    def pages(self):
        return self._iterator

    @property
    def page_count(self):
        return len(self._iterator)

    @classmethod
    def from_args(cls, *args):
        b = cls.__new__(cls)
        pages = []
        for p in args:
            pages.append(Page(p))
        b.__init__(pages)
        return b

    @classmethod
    def from_iter(cls, *args):
        b = cls.__new__(cls)
        pages = []
        for p in chain(*args):
            pages.append(Page(p))
        b.__init__(pages)
        return b

class NavigationOptions:
    """
    Default option class for paginator
    """
    FIRST = ButtonDisplay("⏪")
    LEFT = ButtonDisplay("◀️")
    RIGHT = ButtonDisplay("▶️")
    LAST = ButtonDisplay("⏩")
    DISABLE = ButtonDisplay("🗑️")

    ALL = [FIRST, LEFT, RIGHT, LAST, DISABLE]
    SMALL_PAGERS = [LEFT, RIGHT]
    BIG_PAGERS = [FIRST, LAST]


class Paginator(discord.ui.View):
    def __init__(self, book: Union[Book], users: Union[discord.User, int, list[discord.User], list[int]] = None,
                 options: Optional[NavigationOptions] = None,
                 timeout: Union[int] = 120):
        """
        Custom Paginator
        :param Book book: A book that will be used as an iterator
        :param list[discord.Member] users: A list of all users that are allowed to use this paginator
        :param list[int] users: A list of all user ids that are allowed to use this paginator
        :param None users: Everyone is allowed to use this paginator
        :param NavigationOptions options: The options that will be used to create each button
        :param int timeout: The view's timeout
        :return: The paginator
        :rtype: discord.ui.View
        """
        self.users = []
        if users:
            self.users = users if hasattr(users, '__iter__') else [users]
            self.users = list(map(lambda x: getattr(x, 'id', x), self.users))
        self.page = 0
        self.options = options if options else NavigationOptions()
        self.message = None
        self.book = book

        super().__init__(timeout=timeout)
        table = {
            "First": self.options.FIRST,
            "Left": self.options.LEFT,
            "Right": self.options.RIGHT,
            "Last": self.options.LAST,
            "Delete": self.options.DISABLE,
        }
        for child in self.children:
            child.label, child.emoji, child.style = table[child.label].set_args(child.label, child.emoji, child.style)

    async def _is_owner(self, inter):
        if self.users:
            if inter.user.id not in self.users:
                await inter.response.defer()
                return False
        return True

    async def _turn_page(self, turn: Union[int]):
        if -1 < self.page + turn < self.book.page_count:
            self.page += turn
            return True
        return False

    async def _update_book(self, interaction=None):
        page = self.book.pages[self.page].content
        table = {
            discord.Embed: "embed",
            str: "content"
        }
        if interaction:
            await interaction.response.edit_message(**{table[type(page)]: page})
        elif self.message:
            await self.message.edit(**{table[type(page)]: page})

    @discord.ui.button(label="First", style=discord.ButtonStyle.blurple)
    async def _first(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not (await self._is_owner(interaction)): return
        if self.page > 0:
            self.page = 0
            await self._update_book(interaction)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Left", style=discord.ButtonStyle.blurple)
    async def _left(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not (await self._is_owner(interaction)): return
        paged = await self._turn_page(-1)
        if paged:
            await self._update_book(interaction)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Right", style=discord.ButtonStyle.blurple)
    async def _right(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not (await self._is_owner(interaction)): return
        paged = await self._turn_page(1)
        if paged:
            await self._update_book(interaction)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Last", style=discord.ButtonStyle.blurple)
    async def _last(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not (await self._is_owner(interaction)): return
        l = self.book.page_count - 1
        if self.page < l:
            self.page = l
            await self._update_book(interaction)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red)
    async def _delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not (await self._is_owner(interaction)): return
        await self._disable(interaction)

    async def on_timeout(self) -> None:
        await self._disable()

    async def _disable(self, inter=None):
        self._first.disabled = True
        self._right.disabled = True
        self._left.disabled = True
        self._last.disabled = True
        self._delete.disabled = True
        if inter:
            await inter.response.edit_message(view=self)
        elif self.message:
            await self.message.edit(view=self)
        self.stop()

class DropdownPaginator(discord.ui.View):
    def __init__(self, book: Union[Book], users: Union[discord.User, int, list[discord.User], list[int]] = None,
                 end_button: Union[bool] = False, placeholder: Union[str]='Please select a page', timeout: Union[int] = 120):
        """
        Just like a paginator but with a dropdown menu to select the page from
        :param book: The book that will be used (Book[SelectPage])
        :param users: The users who are allowed to use this Paginator
        :param bool end_button: If an end interaction button should automatically be added
        :param placeholder: The placeholder for when the view hasnt been used before
        :param timeout: The view's timeout
        """
        self.users = users
        if self.users:
            self.users = users if hasattr(users, '__iter__') else [users]
            self.users = list(map(lambda x: getattr(x, 'id', x), self.users))
        super().__init__(timeout=timeout)
        self.book = book
        real_pages = [discord.SelectOption(value=str(i), **book.pages[i].to_kwargs) for i in range(book.page_count)]
        self.select_menu: discord.ui.Select = discord.ui.Select(placeholder=placeholder, options=real_pages)
        self.select_menu.callback = self.callback
        self.last_value = None
        self.end_button = end_button
        self.add_item(self.select_menu)

        if not end_button: self.remove_item(self.end_inter)

    @discord.ui.button(emoji="🗑️", style=discord.ButtonStyle.red)
    async def end_inter(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.stop()
        self.end_inter.disabled = True
        await interaction.response.edit_message(view=None)

    async def callback(self, interaction: discord.Interaction):
        select = self.select_menu
        if self.users and interaction.user.id not in self.users:
            await interaction.response.defer()
            return

        if select.values[0] == self.last_value:
            await interaction.response.defer()
            return

        self.last_value = select.values[0]

        self.clear_items()
        self.add_item(self.select_menu)
        if self.end_button:
            self.add_item(self.end_inter)

        page = self.book.pages[int(select.values[0])]

        if page.buttons and len(page.buttons) > 0:
            for btn in page.buttons:
                self.add_item(btn)

        table = {
            discord.Embed: "embed",
            str: "content"
        }
        add_kwargs = {v: None for v in table.values()}
        add_kwargs[table[type(page.content)]] = page.content
        await interaction.response.edit_message(view=self, **add_kwargs)
