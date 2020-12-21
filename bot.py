import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure, Cog
from person import get_people, get_cards
from credentials import BOTTOKEN
import time
from datetime import timedelta, datetime
import json
import threading
import atexit
from sheets import put_value

bot = commands.Bot(command_prefix='!')

TOKEN = BOTTOKEN
CUBE_LINK = 'https://cubecobra.com/cube/list/a7y'
SHTLINK = 'https://docs.google.com/spreadsheets/d/1uch6JNOBZR5F4bBTIC8FH__pJV5-mdbILee0jeHOhQo/edit?pli=1#gid=354144647'
people = get_people()
reverse_people = [x for x in people[::-1]]
CARDS = get_cards()
CURRENT_PERSON_NUM = 0
CURRENT_PERSON = people[CURRENT_PERSON_NUM]
CURRENT_PERSON_NAME = CURRENT_PERSON.alias
PICK_NUMBER = 1
LAST_PICK_TIME = datetime.now()

state = {
    'current_person_name': CURRENT_PERSON_NAME,
    'current_pick': 1,
    'last_pick_time': datetime.now()
}


def my_converter(o):
    if isinstance(o, datetime):
        return o.__str__()


def get_current_person_and_pick():
    return CURRENT_PERSON, PICK_NUMBER


def swap_lists():
    global people, reverse_people
    swap = people
    people = reverse_people
    reverse_people = swap


def set_current_person(alias):
    global CURRENT_PERSON_NAME, CURRENT_PERSON, CURRENT_PERSON_NUM, people
    if PICK_NUMBER % 2 == 0:
        swap_lists()
    for i, x in enumerate(people):
        if x.alias == alias:
            CURRENT_PERSON_NUM = i
            CURRENT_PERSON = x
            CURRENT_PERSON_NAME = alias
            print(f'Current person set is \n{CURRENT_PERSON}')
            break


def set_next_person(num=1):
    global CURRENT_PERSON_NUM, CURRENT_PERSON, CURRENT_PERSON_NAME, PICK_NUMBER, LAST_PICK_TIME
    count = num
    while count > 0:
        if CURRENT_PERSON_NUM == len(people) - 1:
            swap_lists()
            CURRENT_PERSON_NUM = 0
            CURRENT_PERSON = people[CURRENT_PERSON_NUM]
            CURRENT_PERSON_NAME = CURRENT_PERSON.alias
            PICK_NUMBER += 1
        else:
            CURRENT_PERSON_NUM += 1
            CURRENT_PERSON = people[CURRENT_PERSON_NUM]
            CURRENT_PERSON_NAME = CURRENT_PERSON.alias
        count -= 1
    LAST_PICK_TIME = datetime.now()


@bot.event
async def on_ready():
    global PICK_NUMBER, CURRENT_PERSON, CURRENT_PERSON_NAME, CURRENT_PERSON_NUM
    print('Bot is ready.')
    get_state()
    PICK_NUMBER = state['current_pick']
    set_current_person(state['current_person_name'])
    print(f"GOT THE STATE - {PICK_NUMBER} - {CURRENT_PERSON_NAME}")


class Drafting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pool(self, ctx):
        """\t Get the Current Cube Pool"""
        await ctx.send(CUBE_LINK)

    @commands.command()
    async def sheet(self, ctx):
        """\t Get the Google Sheet"""
        await ctx.send(SHTLINK)

    @commands.command()
    async def pick(self, ctx, *, arg):
        """Syntax: !pick cardname - will put cardname in your column on google sheet and advance"""
        if check_turn(ctx.author.display_name):
            put_value(CURRENT_PERSON.column, PICK_NUMBER, arg)
            print(CURRENT_PERSON.column, PICK_NUMBER, arg)
            await self.advance(ctx)
        else:
            print(arg)
            await ctx.send("👀 It is not your turn to pick yet! 👀")

    @commands.command()
    async def advance(self, ctx, arg=1):
        """\t Moves the draft forward a person and resets the clock - takes optional number to move draft forward that many spaces"""
        set_next_person(arg)
        persist_state()
        await ctx.send(f"It is now <@{CURRENT_PERSON.id}>'s turn to pick "
                       f"- they have until {(datetime.now() + timedelta(hours=24)).strftime('%A at %H:%M %p')}")

    @commands.command()
    async def whoup(self, ctx):
        """Find out who the current person is and ping them"""
        await ctx.send(f"It is <@{CURRENT_PERSON.id}>'s turn to pick "
                       f"- they have until "
                       f"{(LAST_PICK_TIME + timedelta(hours=24)).strftime('%A at %H:%M %p')}")

    @commands.command()
    async def picknum(self, ctx):
        """Get the current pick number"""
        await ctx.send(f"It is currently pick {PICK_NUMBER} out of 45 picks")


bot.add_cog(Drafting(bot))


def check_turn(name):
    if name == CURRENT_PERSON_NAME:
        return True
    return False


def get_state():
    global state, PICK_NUMBER, LAST_PICK_TIME
    with open('last_state.json', 'r') as jsonfile:
        state = json.load(jsonfile)
        state['last_pick_time'] = datetime.strptime(state['last_pick_time'], "%Y-%m-%d %H:%M:%S.%f")
        LAST_PICK_TIME = state['last_pick_time']
        PICK_NUMBER = state['current_pick']


def persist_state():
    global CURRENT_PERSON_NAME, PICK_NUMBER, LAST_PICK_TIME, state
    this_state = \
        {'current_person_name': CURRENT_PERSON_NAME,
         'current_pick': PICK_NUMBER,
         'last_pick_time': LAST_PICK_TIME}
    state = this_state
    with open('last_state.json', 'w+') as jsonfile:
        json.dump(this_state, jsonfile, default=my_converter)


def run_bot():
    bot.run(TOKEN)


t1 = threading.Thread(target=run_bot)
t1.daemon = True
t1.start()

print("Running Bot")


def exit_handler():
    print(f"Persisting state at {time.ctime()}")
    persist_state()
    print("Bot is shutting off")


atexit.register(exit_handler)
while True:
    time.sleep(36000)
    persist_state()
    print("still running")
#
#
# if __name__ == '__main__':
#     main()
