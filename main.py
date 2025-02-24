import discord
from discord.ext import commands
import os
import gmpy2
import hashlib
from struct import pack


WHITELISTED_USERS = {'INSERT_USER_ID'}
DISCORD_TOKEN = 'INSERT_BOT_TOKEN_HERE'

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('ERROR: COMMAND NOT FOUND.')
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('ERROR: MISSING ARGUMENTS.')
    else:
        await ctx.send(f'ERROR OCCURRED: {error}')

def fc_to_pid(friend_code):
    friend_code = friend_code.replace('-', '')
    fc = gmpy2.mpz(friend_code)
    pid = fc & ((1 << 31) - 1)
    return int(pid)

@bot.command()
async def pid(ctx, friend_code: str):
    try:
        pid = fc_to_pid(friend_code)
        await ctx.send(f'{pid} {ctx.author.mention}')
    except Exception as e:
        await ctx.send(f"ERROR CONVERTING THE FC: {e} {ctx.author.mention}")

'''this function is very important if you cannot tell'''
def calc_fc(profile_id, game_id='RMCJ'):
    profile_int = gmpy2.mpz(profile_id)
    profile_bytes = pack('<I', int(profile_int))
    game_id_reversed = game_id[::-1].encode()
    md5_hash = hashlib.md5((profile_bytes + game_id_reversed).ljust(8, b'\0')).digest()
    checksum_byte = md5_hash[0] & 0xfe
    checksum_shifted = gmpy2.mpz(checksum_byte) << 31
    result = profile_int | checksum_shifted
    return int(result)

def format_fc(fc):
    fc_str = str(fc).zfill(12)
    return f"{fc_str[:4]}-{fc_str[4:8]}-{fc_str[8:12]}"

def generate_fcs(start_pid, count, filename='generated_fcs.txt'):
    with open(filename, 'w') as f:
        f.write("# \n")
        f.write("##################################################\n\n")
        for i in range(count):
            current_pid = start_pid + i
            friend_code = calc_fc(current_pid)
            formatted_fc = format_fc(friend_code)
            f.write(f"PID: {current_pid} | FC: {formatted_fc}\n")
    return filename

@bot.command()
async def gen(ctx, pid: int, count: int):
    try:
        if count <= 0:
            await ctx.send(f"{ctx.author.mention}, please try a valid number greater than 0.")
            return
        filename = generate_fcs(pid, count, filename='generated_fcs.txt')
        with open(filename, 'rb') as f:
            await ctx.send(file=discord.File(f, filename))
        os.remove(filename)
    except Exception as e:
        await ctx.send(f"{ctx.author.mention}, ERROR WHILE PROCESSING COMMAND: {e}")

@bot.command()
async def fc(ctx, pid: int):
    try:
        friend_code = calc_fc(pid)
        formatted_fc = format_fc(friend_code)
        await ctx.send(f"{pid}: {formatted_fc} {ctx.author.mention}")
    except Exception as e:
        await ctx.send(f"{ctx.author.mention}, ERROR GENERATING FRIEND CODE: {e}")

def is_whitelisted(ctx):
    return ctx.author.id in WHITELISTED_USERS

@bot.check
async def global_check(ctx):
    if ctx.command.name == 'cmds':
        return True
    if not is_whitelisted(ctx):
        await ctx.send(f"ERROR:{ctx.author.mention}, NOT WHITELISTED.")
        return False
    return True

@bot.command()
async def cmds(ctx):
    embed = discord.Embed(
        title="commands",
        description="beta",
        color=discord.Color.blurple()
    )
    embed.add_field(name="$cmds", value="commands", inline=False)
    embed.add_field(name="$gen <pid> <count>", value="generates fc's (list)", inline=False)
    embed.add_field(name="$pid <fc>", value="fetch the pid for any fc")
    embed.add_field(name="fc <pid>", value="displays the fc for a pid.")
    await ctx.send(embed=embed)



    bot.run(DISCORD_TOKEN)
