import discord
import random
import datetime
from pytz import timezone
import os

dotenv.load_dotenv('.env파일의 경로')


bot = discord.Bot(intents=discord.Intents(guilds=True, voice_states=True, members=True))


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")


@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel and before.channel.name.startswith("Team"):
        if not before.channel.members:
            await before.channel.delete()


@bot.slash_command(
    name="팀갈", description="동일한 통화방에 있는 멤버를 다른 통화방으로 분할합니다."
)
async def divide_team(
    ctx: discord.ApplicationContext,
    팀수: int = discord.Option(description="분할할 팀 수를 정합니다."),
):
    voice_member = []
    teams = {}

    try:
        for member in ctx.author.voice.channel.members:
            if not member.bot:
                voice_member.append(member.id)
    except:
        await ctx.respond("음성 채널에 참여하고 있지 않습니다.")
        return
    
    if int(팀수) > len(voice_member):
        await ctx.respond("분할 될 팀 수가 참가 인원보다 많습니다.")
        return
    
    random.shuffle(voice_member)

    for i in range(0, int(팀수)):
        teams["Team" + str(i + 1)] = []

    while True:
        try:
            for i in range(0, int(팀수)):
                teams["Team" + str(i + 1)].append(voice_member.pop(0))
        except:
            break

    embed = discord.Embed(
        title="팀갈",
        description=f"**{팀수}개**의 팀으로 분할했습니다.",
        color=discord.Colour.from_rgb(181, 27, 117),  # Pycord provides a class with default colors you can choose from
    )

    def team_value(team_number):
        tag = ""
        for index in range(0, len(teams["Team" + str(team_number)])):
            tag += f"<@{teams['Team' + str(team_number)][index]}>\n"
        return tag

    for i in range(0, int(팀수)):
        embed.add_field(
            name=f"Team {i + 1}",
            value=team_value(i + 1),
            inline=True,
        )

    embed.set_footer(text=datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d %p %I시 %M분"))

    class MyView(discord.ui.View):
        @discord.ui.button(emoji="📞", label="가르기", style=discord.ButtonStyle.green)
        async def button_callback(self, button, interaction):
            if interaction.user == ctx.author :
                button.disabled = True

                for i in range(0, int(팀수)):
                    new_channel = await ctx.guild.create_voice_channel(name=f"Team {i + 1}")
                    for index in range(0, len(teams["Team" + str(i + 1)])):
                        await ctx.guild.get_member(
                            teams["Team" + str(i + 1)][index]
                        ).move_to(new_channel)
                        
                await interaction.response.edit_message(view=self)
            else:
                await interaction.response.send_message("명령 시행자만 버튼을 클릭할 수 있습니다.", ephemeral=True)

            

    await ctx.respond(embed=embed, view=MyView())

@bot.slash_command(
    name="모으기", description="모든 통화방에 있는 멤버를 동일한 통화방으로 소집합니다."
)
async def muster(ctx: discord.ApplicationContext):
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.respond("음성 채널에 참여하고 있지 않습니다.")
        return

    await ctx.defer()
    
    for channel in ctx.guild.voice_channels:
        for member in channel.members:
            await ctx.guild.get_member(member.id).move_to(ctx.author.voice.channel)

    try:
        await ctx.followup.send(f"<#{ctx.author.voice.channel.id}>으로 모든 멤버를 소집했습니다.")
    except Exception as e:
        await ctx.followup.send(f"오류가 발생했습니다: {str(e)}")
    
bot.run(os.getenv("Token"))
