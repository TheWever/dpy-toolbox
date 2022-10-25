from discord.ext import commands
import discord

def Default():
    class Default(commands.MinimalHelpCommand):
        async def send_pages(self):
            destination = self.get_destination()
            for page in self.paginator.pages:
                emby = discord.Embed(description=page)
                await destination.send(embed=emby)
    return

def Embedded(bot: commands.Bot):
    class _Embedded(commands.MinimalHelpCommand):
        async def send_pages(self):
            h = ""
            destination = self.get_destination()
            for command in bot.commands:
                h += f"{command.name}: {', '.join(list(command.params.keys()))}\n"
            embed = discord.Embed(title="Help:", description=h, color=discord.Color.blurple())
            await destination.send(embed=embed)

    return _Embedded()