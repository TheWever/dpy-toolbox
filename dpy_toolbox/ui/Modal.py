from typing import Any, Union, Type, Iterable, Callable
from ..core import tokenize, Tokenizer, MISSING
import discord


class QuestioningModal(discord.ui.Modal):
    def __init__(
            self,
            title: str,
            questions: Iterable[str] = MISSING,
            lengths: dict[Union[int, str], int] = MISSING,
            requireds: dict[Union[int, str], bool] = MISSING,
            styles: dict[Union[int, str], discord.TextStyle] = MISSING,
            callback: Callable = None,
            timeout: float = None,
            submit_message: str = "Your modal has been submit and is being processed {user}!",
            error_message: str = "Exception in `QuestioningModal`. Please contact Wever#3255\n{exception}",
            custom_id: str = None,
            **kwargs: str
    ):
        super().__init__(**dict(list(filter(lambda item: item[1], {"title": title, "timeout": timeout, "custom_id": custom_id}.items()))))
        self.callback = callback
        self.submit_message = submit_message
        self.error_message = error_message
        self.questions = kwargs or {i: v for i, v in enumerate(questions)}
        for k, q in self.questions.items():
            length, required, style = (
                lengths.get(k, 300),
                requireds.get(k, True),
                styles.get(q, discord.TextStyle.long)
            )
            inp = discord.ui.TextInput(
                label=q,
                style=style,
                required=required,
                max_length=length,
            )
            self.add_item(inp)

    async def on_submit(self, interaction: discord.Interaction) -> Any:
        if not self.callback:
            return await interaction.response.send_message(tokenize(self.submit_message, **Tokenizer(user=interaction.user)), ephemeral=True)
        return await self.callback(self, interaction)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(tokenize(self.error_message, **Tokenizer(error=error, exception=error)), ephemeral=True)

    @property
    def result(self):
        return {x.label: x.value for x in self.children}

    @property
    def values(self):
        return tuple(self.result.values())

class SingleQuestion(discord.ui.Modal):
    def __init__(
            self,
            question: str = "",
            max_length: int = 30,
            style: discord.TextStyle = discord.TextStyle.short,
            callback: Callable = None
    ):
        self.callback = callback
        super().__init__(title=question)
        self.add_item(
            discord.ui.TextInput(
                label="Answer:",
                style=style,
                required=True,
                max_length=max_length
            )
        )

    async def on_submit(self, interaction: discord.Interaction) -> Any:
        if not self.callback:
            return await interaction.response.send_message(tokenize("Your modal has been submit and is being processed!", **Tokenizer(user=interaction.user)), ephemeral=True)
        return await self.callback(self, interaction)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message("Exception in `SingleQuestion`", ephemeral=True)

    @property
    def result(self):
        return self.children[0].value

    @property
    def value(self):
        return self.result