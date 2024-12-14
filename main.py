
import discord
import datetime
from discord.ext import commands
from discord_components import Button, Select, SelectOption, ComponentsBot, ButtonStyle

bot = ComponentsBot('tb!', help_command=None)

id_category = category  # ID of the category where the bot will create ticket channels
id_channel_ticket_logs = ticket  # ID of the channel where ticket logs will be sent
id_staff_role = staff  # ID of the staff role
embed_color = 0xfcd005  # Embed color in hex


@bot.event
async def on_ready():
    members = sum(guild.member_count - 1 for guild in bot.guilds)

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f'{members} members'
        )
    )
    print('Ready to support ✅')


@bot.command()
@commands.has_permissions(administrator=True)
async def ticket(ctx):
    await ctx.message.delete()

    # Embed title and description
    embed = discord.Embed(title='Tickets', description='Welcome to the tickets system.', color=embed_color)

    # Embed image
    embed.set_image(url='https://i.imgur.com/FoI5ITb.png')

    await ctx.send(
        embed=embed,
        components=[
            Button(
                custom_id='Ticket',
                label="Create a ticket",
                style=ButtonStyle.green,
                emoji='🔧'
            )
        ]
    )


@bot.event
async def on_button_click(interaction):
    canal = interaction.channel
    canal_logs = interaction.guild.get_channel(id_channel_ticket_logs)

    if interaction.component.custom_id == "Ticket":
        await interaction.send(
            components=[
                Select(
                    placeholder="How can we help you?",
                    options=[
                        SelectOption(label="Question", value="question", description='If you have a simple question.',
                                     emoji='❔'),
                        SelectOption(label="Help", value="help", description='If you need help from us.', emoji='🔧'),
                        SelectOption(label="Report", value="report", description='To report a misbehaving user.',
                                     emoji='🚫'),
                    ],
                    custom_id="menu"
                )
            ]
        )

    elif interaction.component.custom_id == 'call_staff':
        embed = discord.Embed(description=f"🔔 {interaction.author.mention} has called the staff.", color=embed_color)
        await canal.send(f'<@&{id_staff_role}>', embed=embed, delete_after=20)

    elif interaction.component.custom_id == 'close_ticket':
        embed = discord.Embed(description=f"⚠️ Are you sure you want to close the ticket?", color=embed_color)
        await canal.send(
            interaction.author.mention,
            embed=embed,
            components=[
                [
                    Button(custom_id='close_yes', label="Yes", style=ButtonStyle.green),
                    Button(custom_id='close_no', label="No", style=ButtonStyle.red)
                ]
            ]
        )

    elif interaction.component.custom_id == 'close_yes':
        await canal.delete()
        embed_logs = discord.Embed(
            title="Tickets",
            description=f"",
            timestamp=datetime.datetime.utcnow(),
            color=embed_color
        )
        embed_logs.add_field(name="Ticket", value=f"{canal.name}", inline=True)
        embed_logs.add_field(name="Closed by", value=f"{interaction.author.mention}", inline=False)
        embed_logs.set_thumbnail(url=interaction.author.avatar_url)
        await canal_logs.send(embed=embed_logs)

    elif interaction.component.custom_id == 'close_no':
        await interaction.message.delete()


@bot.event
async def on_select_option(interaction):
    if interaction.component.custom_id == "menu":

        guild = interaction.guild
        category = discord.utils.get(interaction.guild.categories, id=id_category)
        rol_staff = discord.utils.get(interaction.guild.roles, id=id_staff_role)

        selected_option = interaction.values[0]
        ticket_type = {
            "question": ("❔┃", "Question", "solve your question"),
            "help": ("🔧┃", "Help", "help you with whatever you need"),
            "report": ("🚫┃", "Report", "help you with your report")
        }
        prefix, title, description = ticket_type[selected_option]

        channel = await guild.create_text_channel(
            name=f'{prefix}{interaction.author.name}-ticket',
            category=category
        )

        await channel.set_permissions(guild.default_role, send_messages=False, read_messages=False)
        await channel.set_permissions(interaction.author,
                                      send_messages=True, read_messages=True, add_reactions=True,
                                      embed_links=True, attach_files=True, read_message_history=True,
                                      external_emojis=True)
        await channel.set_permissions(rol_staff,
                                      send_messages=True, read_messages=True, add_reactions=True,
                                      embed_links=True, attach_files=True, read_message_history=True,
                                      external_emojis=True, manage_messages=True)

        await interaction.send(
            f'> The {channel.mention} channel was created to {description}.', delete_after=3
        )

        embed = discord.Embed(
            title=f'{title} - Hi {interaction.author.name}!',
            description=f'In this ticket, we can {description}.\n\n'
                        f"If you can't get help, press the button `🔔 Call staff`.",
            color=embed_color
        )
        embed.set_thumbnail(url=interaction.author.avatar_url)

        await channel.send(
            interaction.author.mention,
            embed=embed,
            components=[
                [
                    Button(custom_id='close_ticket', label="Close ticket", style=ButtonStyle.red, emoji='🔐'),
                    Button(custom_id='call_staff', label="Call staff", style=ButtonStyle.blue, emoji='🔔')
                ]
            ]
        )


bot.run('bottoken')
