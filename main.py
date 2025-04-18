import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import aiohttp
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 봇 토큰 및 환경 설정
TOKEN = os.getenv("TOKEN")
AUTHORIZED_USER_ID = os.getenv("AUTHORIZED_USER_ID")
COMMUNITY_ID = '17253423'  # 인제군 커뮤니티 ID
user_roblox_id_map = {}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 인증 시작 버튼 클릭 처리
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.content == '!인증' and message.author.id == int(AUTHORIZED_USER_ID):
        await message.delete()

        embed = discord.Embed(
            title="인제군에 오신 것을 환영합니다!",
            description="인제군민 등록을 위한 인증을 진행합니다.",
            color=discord.Color.green()
        )

        button = Button(label="➡️시작하기", custom_id="start_verification", style=discord.ButtonStyle.success)

        view = View()
        view.add_item(button)

        await message.channel.send(embed=embed, view=view)

# 버튼 클릭 처리
@bot.event
async def on_interaction(interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.custom_id == "start_verification":
            embed = discord.Embed(
                title="먼저 사용자의 로블록스 ID를 알려주세요!",
                description="입력할 준비가 되셨으면 밑에 있는 '➡️입력하러 가기'를 눌러주세요.",
                color=discord.Color.blue()
            )

            button = Button(label="➡️입력하러 가기", custom_id="open_id_modal", style=discord.ButtonStyle.primary)

            view = View()
            view.add_item(button)

            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        elif interaction.custom_id == "go_back":
            embed = discord.Embed(
                title="먼저 사용자의 로블록스 ID를 알려주세요!",
                description="입력할 준비가 되셨으면 밑에 있는 '➡️입력하러 가기'를 눌러주세요.",
                color=discord.Color.blue()
            )

            button = Button(label="➡️입력하러 가기", custom_id="open_id_modal", style=discord.ButtonStyle.primary)

            view = View()
            view.add_item(button)

            await interaction.response.edit_message(embed=embed, view=view)

        elif interaction.custom_id == "check_community":
            roblox_id = user_roblox_id_map.get(interaction.user.id)

            if not roblox_id:
                return await interaction.response.edit_message(
                    embed=discord.Embed(
                        title="로블록스 ID가 없습니다.",
                        description="처음 단계부터 다시 시작해주세요.",
                        color=discord.Color.red()
                    ),
                    view=None
                )

            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://groups.roblox.com/v1/users/{roblox_id}/groups") as response:
                    data = await response.json()

                    group = next((g for g in data['data'] if str(g['id']) == COMMUNITY_ID), None)

                    if group:
                        embed = discord.Embed(
                            title="인제군 가입을 환영합니다!",
                            description=f"{group['joinedAt']}\n\n인제군에 오신 것을 환영합니다! 현실과 비슷한 맵부터 다양한 시스템들까지! 앞으로 발전할 인제군을 기대해주세요!",
                            color=discord.Color.green()
                        )

                        await interaction.user.send(embed=embed)

                        await interaction.response.edit_message(
                            embed=discord.Embed(
                                title="인증 완료!",
                                description="DM을 확인해주세요!",
                                color=discord.Color.green()
                            ),
                            view=None
                        )
                    else:
                        await interaction.response.edit_message(
                            embed=discord.Embed(
                                title="커뮤니티 사용자 검색에 실패하였습니다.",
                                description="인제군 커뮤니티에 가입되어 있는지 다시 한번 확인해주세요!",
                                color=discord.Color.red()
                            ),
                            view=None
                        )

# 로블록스 ID 모달
@bot.event
async def on_modal_submit(modal):
    if modal.custom_id == "id_modal":
        roblox_username = modal.children[0].value

        async with aiohttp.ClientSession() as session:
            async with session.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [roblox_username]}) as response:
                data = await response.json()

                roblox_id = data['data'][0].get('id') if data['data'] else None

                if not roblox_id:
                    return await modal.send(
                        embed=discord.Embed(
                            title="로블록스 사용자 검색 실패",
                            description="정확한 로블록스 ID를 입력했는지 확인해주세요.",
                            color=discord.Color.red()
                        )
                    )

                user_roblox_id_map[modal.user.id] = roblox_id

                embed = discord.Embed(
                    title="다음으로 커뮤니티 가입을 진행해주세요.",
                    description=f"[인제군 커뮤니티 링크](https://www.roblox.com/ko/communities/{COMMUNITY_ID}/Ulleung-country#!/about)\n\n커뮤니티에 가입한 후 다음을 눌러주세요.",
                    color=discord.Color.blue()
                )

                button_back = Button(label="⬅️이전", custom_id="go_back", style=discord.ButtonStyle.danger)
                button_next = Button(label="➡️다음", custom_id="check_community", style=discord.ButtonStyle.success)

                view = View()
                view.add_item(button_back)
                view.add_item(button_next)

                await modal.response.edit_message(embed=embed, view=view)

# 로블록스 ID 입력 모달 열기
@bot.event
async def on_button_click(interaction):
    if interaction.custom_id == "open_id_modal":
        modal = Modal(title="로블록스 아이디 입력", custom_id="id_modal")
        modal.add_item(TextInput(label="로블록스 아이디를 입력해주세요.", placeholder="예: myRobloxUsername", custom_id="roblox_id", required=True))
        await interaction.response.send_modal(modal)

bot.run(TOKEN)
