from typing import Union, Iterable, Optional, Callable, Coroutine, Any
import discord
from itertools import chain
from ..ui.core import ButtonDisplay, DropdownDisplay, SelectOptionDisplay

ButtonCallback = Callable[[discord.Interaction, discord.ui.Button], Coroutine]  # inter button page

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
    MIDDLE = ButtonDisplay("⏹️")
    RIGHT = ButtonDisplay("▶️")
    LAST = ButtonDisplay("⏩")
    DISABLE = ButtonDisplay("🗑️")

    ALL = [FIRST, LEFT, RIGHT, LAST, DISABLE]
    SMALL_PAGERS = [LEFT, RIGHT]
    BIG_PAGERS = [FIRST, LAST]


class Paginator(discord.ui.View):
    def __init__(
            self,
            book: Union[Book],
            users: Union[discord.User, int, list[discord.User], list[int]] = None,
            options: Optional[NavigationOptions] = None,
            able_to_turn_style: discord.ButtonStyle = None,
            unable_to_turn: ButtonDisplay = None,
            disable_unable: bool = True,
            first_callback: ButtonCallback = None,
            right_callback: ButtonCallback = None,
            left_callback: ButtonCallback = None,
            last_callback: ButtonCallback = None,
            show_page: bool = False,
            timeout: Union[float] = 120):
        """
        Custom Paginator

        :param Book book: A book that will be used as an iterator
        :param list[discord.Member] users: A list of all users that are allowed to use this paginator
        :param list[int] users: A list of all user ids that are allowed to use this paginator
        :param None users: Everyone is allowed to use this paginator
        :param NavigationOptions options: The options that will be used to create each button
        :param float timeout: The view's timeout
        :param discord.ButtonStyle able_to_turn_style:
        :param ButtonDisplay unable_to_turn:
        :param bool disable_unable:  If a button that the user is not able to interact with should be disabled
        :param ButtonCallback first_callback: The callback of the first button which will return to the first page
        :param ButtonCallback right_callback: The callback of the second button which will return to the first page
        :param ButtonCallback left_callback: The callback of the third (or fourth if Middle button) button which will move to the next page
        :param ButtonCallback last_callback: The callback of the fourth (or fifth if Middle button) button which will return to the last page
        :return: The paginator
        :rtype: discord.ui.View
        """
        self.book = book
        self._page = 0
        self.message = None
        self.show_page = show_page
        self.disable_unable = disable_unable

        self.users = []
        if users:
            self.users = users if hasattr(users, '__iter__') else [users]
            self.users = list(map(lambda x: getattr(x, 'id', x), self.users))

        self.options = options if options else NavigationOptions()

        self.able_to_turn_style = able_to_turn_style or discord.ButtonStyle.green
        self.unable_to_turn = unable_to_turn or ButtonDisplay(label='...', color=discord.ButtonStyle.red)

        self.left_callback = left_callback or self.default_callback_wrapper(lambda: self._page - 1)
        self.right_callback = right_callback or self.default_callback_wrapper(lambda: self._page + 1)

        self.first_callback = first_callback or self.default_callback_wrapper(lambda: 0)
        self.last_callback = last_callback or self.default_callback_wrapper(lambda: self.book.page_count - 1)

        super().__init__(timeout=timeout)

        self._middle.disabled = True
        if self.show_page:
            self.options.LEFT = self.unable_to_turn
            self.options.MIDDLE.set_kwargs(label="1")
            self.options.RIGHT.set_kwargs(label="2")

        table = {
            "First": self.options.FIRST,
            "Left": self.options.LEFT,
            "Middle": self.options.MIDDLE,
            "Right": self.options.RIGHT,
            "Last": self.options.LAST,
            "Delete": self.options.DISABLE,
        }
        for child in self.children:
            child.label, child.emoji, child.style = table[child.label].set_args(child.label, child.emoji, child.style)

        if self.show_page:
            self._update_buttons(self._page)

    async def get_message(self, message: Union[str, discord.Embed]):
        return message

    async def _is_owner(self, inter):
        if self.users:
            if inter.user.id not in self.users:
                await inter.response.defer()
                return False
        return True

    def _update_buttons(self, final_page):
        bias_page = final_page + 1

        self._left.style, self._middle.style, self._right.style = 3 * [self.able_to_turn_style]

        self._left.label = str(bias_page - 1)
        self._middle.label = str(bias_page)
        self._right.label = str(bias_page + 1)

        stylish_checks = (
            (self._right, final_page == self.book.page_count - 1),
            (self._left, final_page < 1)
        )

        for btn, check in stylish_checks:
            if check:
                btn.label, btn.emoji, btn.style = self.unable_to_turn.to_args
            btn.disabled = True if self.disable_unable and check else False

    async def _turn_page(self, turn: Union[int]):
        if -1 < turn < self.book.page_count:
            self._page = turn
            return True
        return False

    def default_callback_wrapper(self, turn: Callable):
        async def default_callback(inter: discord.Interaction, button: discord.ui.Button):
            if not (await self._is_owner(inter)):
                return

            final_page = turn()
            if self._page == final_page:
                return await inter.response.defer()

            turned_page = await self._turn_page(final_page)

            if self.show_page:
                self._update_buttons(final_page)

            if turned_page:
                await self._update_book(inter)
            else:
                await inter.response.defer()

        return default_callback

    @property
    def page(self):
        return self.book.pages[self._page]

    async def _update_book(self, interaction=None):
        await self.on_update(interaction, self._page)
        page = self.book.pages[self._page].content
        table = {
            discord.Embed: "embed",
            str: "content"
        }
        if interaction:
            await interaction.response.edit_message(**{table[type(page)]: await self.get_message(page)}, view=self)
            if interaction.message:
                self.message = interaction.message
        elif self.message:
            await self.message.edit(**{table[type(page)]: await self.get_message(page)}, view=self)

    @discord.ui.button(label="First", style=discord.ButtonStyle.blurple)
    async def _first(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.first_callback(interaction, button)

    @discord.ui.button(label="Left", style=discord.ButtonStyle.blurple)
    async def _left(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.left_callback(interaction, button)

    @discord.ui.button(label="Middle", style=discord.ButtonStyle.blurple)
    async def _middle(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label="Right", style=discord.ButtonStyle.blurple)
    async def _right(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.right_callback(interaction, button)

    @discord.ui.button(label="Last", style=discord.ButtonStyle.blurple)
    async def _last(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.last_callback(interaction, button)

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red)
    async def _delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not (await self._is_owner(interaction)): return
        await self._disable(interaction)

    async def on_update(
            self, interaction: discord.Interaction,
            page: int
    ) -> None:
        pass

    async def on_timeout(self) -> None:
        await self._disable()

    async def _disable(self, inter=None):
        for btn in self.children:
            btn.disabled = True
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