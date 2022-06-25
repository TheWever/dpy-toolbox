import os
import discord
from discord.ext import commands
from dpy_toolbox import Bot, Sink, MP3Sink, VirtualSink, to_SinkVoiceClient, to_SinkVoiceChannel

bot = Bot(command_prefix='!', intents=discord.Intents.all())
bot.connections = {}
TOKEN = ''

@bot.event
async def on_ready():
    print('test')

@bot.command()
async def start(ctx: commands.Context):
    """
    Record your voice!
    """
    voice = ctx.author.voice
    if not voice:
        return await ctx.reply("You're not in a vc right now")
    vc = await to_SinkVoiceChannel(voice.channel)
    vc = await vc.connect()
    bot.connections.update({ctx.guild.id: vc})
    vc.listen(
        Sink(encoding="mp3", output_path='tmp/'),
        finished_callback,
        ctx.channel,
    )
    await ctx.reply("The recording has started!")


async def finished_callback(sink, channel: discord.TextChannel, *args):
    recorded_users = [
        f"<@{user_id}>"
        for user_id, audio in sink.audio_data.items()
    ]
    await sink.vc.disconnect()
    files = [discord.File(audio.file_name, f"{user_id}.{sink.encoding}") for user_id, audio in sink.audio_data.items()]
    await channel.send(f"Finished! Recorded audio for {', '.join(recorded_users)}.", files=files)


@bot.command()
async def stop(ctx):
    """
    Stop recording.
    """
    if ctx.guild.id in bot.connections:
        vc = bot.connections[ctx.guild.id]
        vc.stop_listening()
        del bot.connections[ctx.guild.id]
        await ctx.delete()
    else:
        await ctx.reply("Not recording in this guild.")


bot.run(TOKEN)