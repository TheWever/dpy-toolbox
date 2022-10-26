from discord.ext import commands
from dpy_toolbox.core.errors import NotAllowed

def is_user(*args):
    """
    The old is_user check that has been removed from discord.py

    :param int args: The id of each user that is allowed to use this command
    :return: The new check which will only call the command on a pass and raises otherwise

    :raises NotAllowed: If the user who called the function is not in args
    """
    user_ids = [int(x) for x in args]

    async def predicate(ctx: commands.Context) -> bool:
        """
        :meta private:
        """
        if ctx.author.id not in user_ids:
            raise NotAllowed(f"{ctx.author.id} is not allowed to use {ctx.invoked_with}")
        return True

    return commands.core.check(predicate)