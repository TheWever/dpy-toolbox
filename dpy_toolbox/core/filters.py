import discord
from typing import Optional, Union, List, Set, Tuple, Callable, Any

def ensure_set(s: Optional[Union[str, List[str], Tuple[str], Set[str]]]) -> List[str]:
    """
    :meta private:
    """
    # Ref: https://stackoverflow.com/a/56641168/
    return s if isinstance(s, set) else set(s) if isinstance(s, (tuple, list)) else [] if s is None else [s]

format_filter_arg = lambda obj, type: ensure_set(list(map(type, obj)))

class MessageFilter:
    """
    A simple filter for messages

    :param list[int] authors: The message must be send by any of these users
    :param list[int] guild_ids: The message but be located in any of these guilds
    :param list[int] channel_ids: The message but be located in any of these channels
    :param list[int] mentions_all: The message must mention all of these users
    :param list[int] mentions_any: The message must mention any of these users
    :param list[str] match_content: The exact content the message must include
    :param list[str] in_content: The content that must be found in the message
    :param list[str] startswith_content: The content the message must start with
    :param list[str] endswith_content: The content the message must end with
    :param list[int] not_authors: Users that must not have written this message
    :param list[int] not_guild_ids: The guilds that will be filtered
    :param list[int] not_channel_ids: The channels that will be filtered
    :param list[int] not_mentions: The users the message must not mention
    :param list[str] not_match_content: The content the message must not include
    :param list[str] not_in_content: The content that must not be found  in the message
    :param list[str] not_startswith_content: The content the message must not start with
    :param list[str] not_endswith_content: The content the message must not end with
    :param int account_type:
        The type of account the author has:
        0 Bots are excluded / users only
        1 Users are excluded / bots only
        2 No exclusion / everyone

    :return: The message filter that can be used to filter messages
    """
    def __init__(
            self,
            authors: Union[int, list[int]] = None,
            guild_ids: Union[int, list[int]] = None,
            channel_ids: Union[int, list[int]] = None,
            mentions_all: Union[int, list[int]] = None,
            mentions_any: Union[int, list[int]] = None,
            match_content: Union[str, list[str]] = None,
            in_content: Union[str, list[str]] = None,
            startswith_content: Union[str, list[str]] = None,
            endswith_content: Union[str, list[str]] = None,
            not_authors: Union[int, list[int]] = None,
            not_guild_ids: Union[int, list[int]] = None,
            not_channel_ids: Union[int, list[int]] = None,
            not_mentions: Union[str, list[str]] = None,
            not_match_content: Union[str, list[str]] = None,
            not_in_content: Union[str, list[str]] = None,
            not_startswith_content: Union[str, list[str]] = None,
            not_endswith_content: Union[str, list[str]] = None,
            account_type: int = 2,
    ):
        self.all_filters = {
            "authors": authors, "guild_ids": guild_ids, "channel_ids": channel_ids, "mentions_all": mentions_all,
            "mentions_any": mentions_any, "match_content": match_content, "in_content": in_content,
            "startswith_content": startswith_content, "endswith_content": endswith_content,
            "not_authors": not_authors, "not_guild_ids": not_guild_ids, "not_channel_ids": not_channel_ids,
            "not_mentions": not_mentions, "not_match_content": not_match_content,
            "not_in_content": not_in_content, "not_startswith_content": not_startswith_content, "not_endswith_content": not_endswith_content,
            "account_type": account_type
        }
        self.filters = self.get_filter(**self.all_filters)

    def get_filter(
            self,
            authors: Union[int, list[int]] = None,
            guild_ids: Union[int, list[int]] = None,
            channel_ids: Union[int, list[int]] = None,
            mentions_all: Union[int, list[int]] = None,
            mentions_any: Union[int, list[int]] = None,
            match_content: Union[int, list[int]] = None,
            in_content: Union[str, list[str]] = None,
            startswith_content: Union[str, list[str]] = None,
            endswith_content: Union[str, list[str]] = None,
            not_authors: Union[int, list[int]] = None,
            not_guild_ids: Union[int, list[int]] = None,
            not_channel_ids: Union[int, list[int]] = None,
            not_mentions: Union[str, list[str]] = None,
            not_match_content: Union[str, list[str]] = None,
            not_in_content: Union[str, list[str]] = None,
            not_startswith_content: Union[str, list[str]] = None,
            not_endswith_content: Union[str, list[str]] = None,
            account_type: int = 2,
    ):
        """
        A simple filter for messages

        :param list[int] authors: The message must be send by any of these users
        :param list[int] guild_ids: The message but be located in any of these guilds
        :param list[int] channel_ids: The message but be located in any of these channels
        :param list[int] mentions_all: The message must mention all of these users
        :param list[int] mentions_any: The message must mention any of these users
        :param list[str] match_content: The exact content the message must include
        :param list[str] in_content: The content that must be found in the message
        :param list[str] startswith_content: The content the message must start with
        :param list[str] endswith_content: The content the message must end with
        :param list[int] not_authors: Users that must not have written this message
        :param list[int] not_guild_ids: The guilds that will be filtered
        :param list[int] not_channel_ids: The channels that will be filtered
        :param list[int] not_mentions: The users the message must not mention
        :param list[str] not_match_content: The content the message must not include
        :param list[str] not_in_content: The content that must not be found  in the message
        :param list[str] not_startswith_content: The content the message must not start with
        :param list[str] not_endswith_content: The content the message must not end with
        :param int account_type:
            The type of account the author has:
            0 Bots are excluded / users only
            1 Users are excluded / bots only
            2 No exclusion / everyone
        """
        filters = {
                "authors": (lambda m: any([author_id in format_filter_arg(authors, int)] for author_id in authors)) if authors else None,
                "guild_ids": (lambda m: any([guild_id in format_filter_arg(guild_ids, int)] for guild_id in guild_ids)) if guild_ids else None,
                "channel_ids": (lambda m: any([channel_id in format_filter_arg(channel_ids, int)] for channel_id in channel_ids)) if channel_ids else None,
                "mentions_all": (lambda m: all([mention in format_filter_arg(mentions_all, int)] for mention in m.mentions)) if mentions_all else None,
                "mentions_any": (lambda m: any([mention in format_filter_arg(mentions_any, int)] for mention in m.mentions)) if mentions_any else None,
                "match_content": (lambda m: any(txt == m.content for txt in ensure_set(match_content))) if match_content else None,
                "in_content": (lambda m: any(txt in m.content for txt in in_content)) if in_content else None,
                "startswith_content": (lambda m: any(txt.startswith(m.content) for txt in ensure_set(startswith_content))) if startswith_content else None,
                "endswith_content": (lambda m: any(txt.endswith(m.content) for txt in ensure_set(endswith_content))) if endswith_content else None,
                "not_authors": (lambda m: not any([author_id in format_filter_arg(not_authors, int)] for author_id in not_authors)) if not_authors else None,
                "not_guilds": (lambda m: not any([guild_id in format_filter_arg(not_guild_ids, int)] for guild_id in not_guild_ids)) if not_guild_ids else None,
                "not_channel": (lambda m: not any([channel_id in format_filter_arg(not_channel_ids, int)] for channel_id in not_channel_ids)) if not_channel_ids else None,
                "not_mentions": (lambda m: not any([mention in format_filter_arg(not_mentions, int)] for mention in m.mentions)) if not_mentions else None,
                "not_match_content": (lambda m: not any(txt == m.content for txt in ensure_set(not_match_content))) if not_match_content else None,
                "not_in_content": (lambda m: not any(txt in m.content for txt in ensure_set(not_in_content))) if not_in_content else None,
                "not_startswith_content": (lambda m: not any(txt.startswith(m.content) for txt in ensure_set(not_startswith_content))) if not_startswith_content else None,
                "not_endswith_content": (lambda m: not any(txt.endswith(m.content) for txt in ensure_set(not_endswith_content))) if not_endswith_content else None,
                "account_type": (lambda m: m.author.bot if account_type == 1 else not m.author.bot) if account_type != 2 else None
            }
        return dict(filter(lambda item: item[1] is not None, filters.items()))

    def set_filter(self, **kwargs: Callable):
        """
        Set the filters attribute
        :param Callable kwargs: Will replace key in filters with value
        """
        for k, v in kwargs:
            self.filters[k] = v

    def set_filter_arg(self, **kwargs: Any):
        """
        Set the filters attribute

        :param Callable kwargs: Will replace key in filters with value
        """
        for k, v in kwargs:
            self.all_filters[k] = v

    def __iter__(self):
        return self.filters

    def __call__(self, msg: discord.Message):
        return all([x(msg) for x in self.filters.values()])
