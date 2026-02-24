from enum import unique
import discord
from discord import app_commands 
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions
from PIL import Image, ImageDraw, ImageFont
import requests
import io
import random
from datetime import datetime
import pytz
from io import BytesIO

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.members = True
intents.message_content = True  

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

@bot.command()
async def makeinvite(ctx):
    if ctx.guild:
        invite = await ctx.channel.create_invite(max_age=86400, max_uses=1)
        await ctx.send(f'Here is the invite link: {invite.url}')
    else:
        await ctx.send('This command can only be used in a server.')

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    try:
        await member.ban(reason=reason)
        await ctx.send(f'{member.display_name} has been banned.')
    except discord.Forbidden:
        await ctx.send("I don't have permission to ban members.")
    except discord.HTTPException:
        await ctx.send("An error occurred while trying to ban the member.")

@bot.command()
async def invite(ctx, friend: discord.User):
    invite = await ctx.channel.create_invite(max_age=86400, max_uses=1)
    await friend.send(f'Here is the invite link to the server: {invite.url}')

@invite.error
async def invite_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Please provide a valid user mention or user ID.")

@bot.command()
async def dm(ctx, friend: discord.User, *, message: str):
    try:
        await friend.send(message)
        await ctx.send(f'Message sent to {friend.mention}.')
    except discord.Forbidden:
        await ctx.send("I'm unable to send a message to that user.")

@dm.error
async def dm_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please provide a user mention or user ID and a message.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please provide a valid user mention or user ID.")

@bot.command()
async def delete(ctx, amount: int):
    if amount <= 0:
        await ctx.send("Please specify a valid number of messages to delete.")
        return
    
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"Deleted {len(deleted) - 1} messages.", delete_after=5)

def is_owner(ctx):
    return ctx.author.id == ctx.guild.owner_id

@bot.command()
async def go_die(ctx):
    if ctx.author.guild_permissions.administrator:
        for channel in ctx.guild.channels:
            await channel.delete()
        for role in ctx.guild.roles:
            await role.delete()
        for member in ctx.guild.members:
            try:
                await member.kick()
            except:
                pass
        await ctx.send('Goodbye cruel world....')
    else:
        await ctx.send('You do not have permission to use this command.')

WELCOME_CHANNEL_ID = 1244277809082404975

@bot.event
async def on_member_join(member):
    card = create_welcome_card(member)
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        with io.BytesIO() as image_binary:
            card.save(image_binary, 'PNG')
            image_binary.seek(0)
            await channel.send(file=discord.File(fp=image_binary, filename='welcome.png'))

def create_random_ip():
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"

def create_welcome_card(member):
    # Load the background image
    background_path = r'path to background in new folder'  # Update with your image path and extension
    background = Image.open(background_path)
    background = background.resize((1100, 500))  # Resize to fit card dimensions if necessary

    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype("arial.ttf", 43)
    
    random_ip = create_random_ip()

    username_with_discriminator = f"{member.name}#{member.discriminator}"

    draw.text((160, 315), f"{username_with_discriminator} just joined the server!", fill=(211, 211, 211), font=font)
    draw.text((70, 375), f"User ID: {member.id}", fill=(105, 105, 105), font=font)
    draw.text((70, 420), f"Your IP: {random_ip}", fill=(105, 105, 105), font=font)

    # Load the profile picture
    pfp_url = member.avatar.url if member.avatar else None
    if pfp_url:
        response = requests.get(pfp_url)
        pfp = Image.open(BytesIO(response.content))

        # Resize the profile picture to fit the card
        pfp_size = (230, 230)  # Adjust size as needed
        pfp = pfp.resize(pfp_size)

        # Create a mask for the circular shape
        mask = Image.new("L", pfp_size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0) + pfp_size, fill=255)

        # Apply the mask to the profile picture
        pfp = Image.composite(pfp, Image.new("RGB", pfp_size, (6, 6, 8)), mask)

        # Paste the profile picture onto the background
        pfp_position = (435, 50)  # Adjust position as needed
        background.paste(pfp, pfp_position)
    
    return background

@bot.event
async def on_member_remove(member):
    try:
        await member.send(f"Goodbye **{member.name}**, we are not sorry to see you leave!")
    except discord.Forbidden:
        print(f"Could not send DM to {member.name}")
    
    channel = bot.get_channel(111111111111111111)
    if channel:
        await channel.send(f"Goodbye **{member.name}**, we are not sorry to see you leave!")
    else:
        print(f"Could not find channel with ID {111111111111111111}")

NOTIFICATION_CHANNEL_ID = 111111111111111  #add your channel id
excluded_user_ids = [11111111111,1111111111111111 ] #add your ids on which bot cant spyyyyyyyyyy

@bot.event
async def on_message(message):
    # Check if the message is a DM and not sent by the bot itself
    if isinstance(message.channel, discord.DMChannel) and message.author != bot.user:
        # Exclude specified user IDs' DMs from being sent to the notification channel
        if message.author.id not in excluded_user_ids:
            channel = bot.get_channel(NOTIFICATION_CHANNEL_ID)
            if channel:
                await channel.send(f"Received a DM from {message.author.name}#{message.author.discriminator} (ID: {message.author.id}): {message.content}")

    # Check if the message contains attachments and is not sent by the bot itself
    if message.author != bot.user and message.attachments:
        for attachment in message.attachments:
            channel = bot.get_channel(NOTIFICATION_CHANNEL_ID)
            await channel.send(f"Attachment from {message.author.display_name}: {attachment.url}")

    await bot.process_commands(message)

@bot.command()
async def status(ctx, mode: str):
    modes = {
        'online': discord.Status.online,
        'idle': discord.Status.idle,
        'dnd': discord.Status.dnd,
        'invisible': discord.Status.invisible
    }

    if mode.lower() in modes:
        await bot.change_presence(status=modes[mode.lower()])
        await ctx.send(f'Status changed to {mode.lower()}')
    else:
        await ctx.send('Invalid status mode. Try online, idle, dnd, or invisible.')

@bot.command()
async def openup(ctx):
    commands_list = [command.name for command in bot.commands]
    commands_string = "\n".join(commands_list)
    await ctx.send(f"Here are all my commands:\n```{commands_string}```")

@bot.command()
async def kick(ctx, server_id: int, user_id: int):
    """
    Kicks a user from a specific server.

    Parameters:
        - server_id: The ID of the server from which to kick the user.
        - user_id: The ID of the user to kick.
    """
    # Get the server object
    server = bot.get_guild(server_id)
    if server is None:
        await ctx.send("Invalid server ID.")
        return
    
    # Get the user object
    user = await bot.fetch_user(user_id)
    if user is None:
        await ctx.send("Invalid user ID.")
        return

    # Check if the bot has permissions to kick members
    if ctx.guild.me.guild_permissions.kick_members:
        try:
            await server.kick(user)
            await ctx.send(f"{user.name} has been kicked from the server.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to kick members from that server.")
    else:
        await ctx.send("I don't have permission to kick members.")

@bot.command()
async def auditlog(ctx, server_id: int, channel_id: int):
    """
    Fetches and displays the audit log history in a specific channel.

    Parameters:
        - server_id: The ID of the server from which to fetch the audit log.
        - channel_id: The ID of the channel in which to display the audit log.
    """
    # Get the server object
    server = bot.get_guild(server_id)
    if server is None:
        await ctx.send("Invalid server ID.")
        return
    
    # Get the channel object
    channel = server.get_channel(channel_id)
    if channel is None:
        await ctx.send("Invalid channel ID.")
        return

    # Fetch the audit log
    async for entry in server.audit_logs(limit=10):  # Limiting to 10 entries for demonstration
        await channel.send(f"{entry.user} did {entry.action} to {entry.target}")

@bot.command()
async def deletes(ctx, server_id: int, channel_id: int, amount: int):
    """
    Deletes a specified number of messages from a channel in another server.

    Parameters:
        - server_id: The ID of the server from which to delete messages.
        - channel_id: The ID of the channel from which to delete messages.
        - amount: The number of messages to delete.
    """
    # Get the server object
    server = bot.get_guild(server_id)
    if server is None:
        await ctx.send("Invalid server ID.")
        return
    
    # Get the channel object
    channel = server.get_channel(channel_id)
    if channel is None:
        await ctx.send("Invalid channel ID.")
        return

    # Check if the bot has permissions to delete messages
    if channel.permissions_for(server.me).manage_messages:
        try:
            # Delete messages from the channel
            deleted = await channel.purge(limit=amount)
            await ctx.send(f"Deleted {len(deleted)} messages from {channel.name}.")
        except discord.Forbidden:
            await ctx.send("I don't have permission to delete messages from that channel.")
    else:
        await ctx.send("I don't have permission to delete messages.")

@bot.command()
async def sendword(ctx, server_id: int, channel_id: int, *, message: str):
    """
    Sends a message to a specific channel in another server.

    Parameters:
        - server_id: The ID of the server to send the message to.
        - channel_id: The ID of the channel to send the message to.
        - message: The message to send.
    """
    # Get the server object
    server = bot.get_guild(server_id)
    if server is None:
        await ctx.send("Invalid server ID.")
        return
    
    # Get the channel object
    channel = server.get_channel(channel_id)
    if channel is None:
        await ctx.send("Invalid channel ID.")
        return

    # Send the message to the channel
    await channel.send(message)
    await ctx.send(f"Message sent to {channel.name} in {server.name}.")

LOG_CHANNEL_ID = 111111111111111    #add your channel id

async def send_log_embed(channel, title, description, color=discord.Color.default()):
    current_time = datetime.now(pytz.timezone('Asia/Karachi'))  # Get current time in Pakistan timezone
    formatted_time = current_time.strftime("%m/%d/%Y %I:%M %p")  # Format the time as desired
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=f"{formatted_time}")  # Add formatted time to the footer
    await channel.send(embed=embed)

@bot.event
async def on_message_delete(message):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel and not message.author.bot:
        embed = discord.Embed(title="Message Deleted", description=f"Message deleted from {message.channel.mention} by {message.author.mention}:", color=discord.Color.brand_red())

        # Add message content to the embed
        embed.add_field(name="Content", value=message.content or "*No content*", inline=False)

        # Add attachments to the embed
        for attachment in message.attachments:
            if attachment.url.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                embed.set_image(url=attachment.url)
            elif attachment.url.lower().endswith((".mp4", ".mov", ".avi", ".webm")):
                embed.add_field(name="Video Attachment", value=f"[Watch here]({attachment.url})", inline=False)
            else:
                embed.add_field(name="Attachment", value=f"[Download]({attachment.url})", inline=False)

        await channel.send(embed=embed)

@bot.event
async def on_member_update(before, after):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:
        embed = discord.Embed(title="Member Update", color=discord.Color.from_rgb(95, 158, 160))

        changes = []
        if before.nick != after.nick:
            changes.append(f"Nickname changed from {before.nick} to {after.nick}")
        if before.roles != after.roles:
            roles_added = set(after.roles) - set(before.roles)
            roles_removed = set(before.roles) - set(after.roles)
            if roles_added:
                changes.append(f"Roles added: {', '.join(role.name for role in roles_added)}")
            if roles_removed:
                changes.append(f"Roles removed: {', '.join(role.name for role in roles_removed)}")

        if changes:
            mention = after.mention  # Mention the member after the changes are applied
            embed.description = f"{mention}\n" + "\n".join(changes)
            await channel.send(embed=embed)

@bot.event
async def on_voice_state_update(member, before, after):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:
        if before.channel is None and after.channel is not None:
            await send_log_embed(channel, "📥 Voice Channel Join", f"{member.mention} joined voice channel\n```\n{after.channel.name}\n```", discord.Color.from_rgb(220, 220, 220))
        elif before.channel is not None and after.channel is None:
            await send_log_embed(channel, "📤 Voice Channel Leave", f"{member.mention} left voice channel```{before.channel.name}```", discord.Color.from_rgb(0, 0, 0))

bot.run('Bot Token')            #Replace bot token with your bot token
