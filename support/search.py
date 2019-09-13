from support.bcolors import Bcolors

class Search:

    @staticmethod
    def search_user(ctx, search):
        print(Bcolors.OKBLUE + f'searching in {ctx.guild.name} for {search}')

        # Search by discord user
        user = next((i for i in ctx.guild.members if str(search).lower() in str(i).lower()), None)
        if (user == None):
            # Search by discord user nickname
            user = next((i for i in ctx.guild.members if str(search).lower() in str(i.display_name).lower()), ctx.author)
        return user
