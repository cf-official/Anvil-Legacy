from support.bcolors import Bcolors
from datetime import datetime
import time

# Search for a specific user and return it
class Search:
    @staticmethod
    def search_user(ctx, search):
        print(Bcolors.OKBLUE + f'searching in {ctx.guild.name} for {search}')

        # Search by discord user
        user = next((i for i in ctx.guild.members if str(search).lower() in str(i).lower()), None)
        if user is None:
            # Search by discord user nickname
            user = next((i for i in ctx.guild.members if str(search).lower() in str(i.display_name).lower()), ctx.author)
        return user


# Allows for creation of a dict that allows attributes to be called instead of keys
class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def difference_in_minutes(d1, d2):
    # Convert to Unix timestamp
    d1_ts = time.mktime(d1.timetuple())
    d2_ts = time.mktime(d2.timetuple())

    # They are now in seconds, subtract and then divide by 60 to get minutes.
    difference = int(d2_ts - d1_ts) / 60
    return difference
