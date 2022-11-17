# -*- coding: utf-8 -*-

from typing import Optional

import discord
from discord.ext import commands

from dpy_toolbox import Bot, CustomContext, UnvirtualSink, to_SinkVoiceChannel

bot = Bot(command_prefix='!', intents=discord.Intents.all())
TOKEN = ''  # BAD


@bot.event
async def on_ready() -> None:
    print('test')


@bot.command()
async def start(ctx: commands.Context) -> Optional[discord.Message]:
    """
    Record your voice!
    """
    voice = ctx.author.voice
    if not voice:
        return await ctx.reply("You're not in a vc right now")
    vc = await to_SinkVoiceChannel(voice.channel)
    vc = await vc.connect()
    vc.listen(
        UnvirtualSink(),  # more convenient: Sink(encoding="mp3", output_path='tmp/'),
        finished_callback,
        ctx.channel,
    )
    await ctx.reply("The recording has started!")


async def finished_callback(sink, channel: discord.TextChannel) -> None:
    recorded_users = [
        f"<@{user_id}>"
        for user_id, audio in sink.audio_data.items()
    ]
    await sink.vc.disconnect()
    files = [discord.File(audio, f"{user_id}.{sink.encoding}") for user_id, audio in sink.output.items()]
    await channel.send(f"Finished! Recorded audio for {', '.join(recorded_users)}.", files=files)


@bot.command()
async def stop(ctx: CustomContext[Bot]) -> None:
    """
    Stop recording.
    """
    if vc := ctx.guild.voice_client:
        vc.stop_listening()
        await ctx.delete()
    else:
        await ctx.reply("Not recording in this guild.")

bot.run(TOKEN)
