# 이름: roblox-verification.js
# 필요 모듈: discord.js, node-fetch, dotenv

const { Client, GatewayIntentBits, Partials, EmbedBuilder, ButtonBuilder, ActionRowBuilder, ButtonStyle, ModalBuilder, TextInputBuilder, TextInputStyle, Events } = require('discord.js');
const fetch = require('node-fetch');
require('dotenv').config();

const client = new Client({
  intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent],
  partials: [Partials.Message, Partials.Channel, Partials.Reaction],
});

const AUTHORIZED_USER_ID = process.env.AUTHORIZED_USER_ID;
const COMMUNITY_ID = '17253423'; // 인제군 커뮤니티 ID

const userRobloxIdMap = new Map();

client.on('messageCreate', async (message) => {
  if (message.content === '!인증' && message.author.id === AUTHORIZED_USER_ID) {
    await message.delete();

    const embed = new EmbedBuilder()
      .setTitle('인제군에 오신 것을 환영합니다!')
      .setDescription('인제군민 등록을 위한 인증을 진행합니다.')
      .setColor('Green');

    const startButton = new ButtonBuilder()
      .setCustomId('start_verification')
      .setLabel('➡️시작하기')
      .setStyle(ButtonStyle.Success);

    const row = new ActionRowBuilder().addComponents(startButton);

    await message.channel.send({ embeds: [embed], components: [row] });
  }
});

client.on(Events.InteractionCreate, async (interaction) => {
  if (interaction.isButton()) {
    if (interaction.customId === 'start_verification') {
      const embed = new EmbedBuilder()
        .setTitle('먼저 사용자의 로블록스 ID를 알려주세요!')
        .setDescription("입력할 준비가 되셨으면 밑에 있는 '➡️입력하러 가기'를 눌러주세요.")
        .setColor('Blue');

      const button = new ButtonBuilder()
        .setCustomId('open_id_modal')
        .setLabel('➡️입력하러 가기')
        .setStyle(ButtonStyle.Primary);

      const row = new ActionRowBuilder().addComponents(button);

      await interaction.reply({ ephemeral: true, embeds: [embed], components: [row] });
    }

    if (interaction.customId === 'go_back') {
      const embed = new EmbedBuilder()
        .setTitle('먼저 사용자의 로블록스 ID를 알려주세요!')
        .setDescription("입력할 준비가 되셨으면 밑에 있는 '➡️입력하러 가기'를 눌러주세요.")
        .setColor('Blue');

      const button = new ButtonBuilder()
        .setCustomId('open_id_modal')
        .setLabel('➡️입력하러 가기')
        .setStyle(ButtonStyle.Primary);

      const row = new ActionRowBuilder().addComponents(button);

      await interaction.update({ embeds: [embed], components: [row] });
    }

    if (interaction.customId === 'check_community') {
      const robloxId = userRobloxIdMap.get(interaction.user.id);

      if (!robloxId) {
        return interaction.update({
          embeds: [
            new EmbedBuilder()
              .setTitle('로블록스 ID가 없습니다.')
              .setDescription('처음 단계부터 다시 시작해주세요.')
              .setColor('Red')
          ],
          components: [],
        });
      }

      try {
        const response = await fetch(`https://groups.roblox.com/v1/users/${robloxId}/groups`);
        const data = await response.json();

        const group = data.data.find(g => g.id.toString() === COMMUNITY_ID);

        if (group) {
          const embed = new EmbedBuilder()
            .setTitle('인제군 가입을 환영합니다!')
            .setDescription(`${group.joinedAt}\n\n인제군에 오신 것을 환영합니다! 현실과 비슷한 맵부터 다양한 시스템들까지! 앞으로 발전할 인제군을 기대해주세요!`)
            .setColor('Green');

          await interaction.user.send({ embeds: [embed] });

          await interaction.update({
            embeds: [
              new EmbedBuilder()
                .setTitle('인증 완료!')
                .setDescription('DM을 확인해주세요!')
                .setColor('Green')
            ],
            components: [],
          });
        } else {
          await interaction.update({
            embeds: [
              new EmbedBuilder()
                .setTitle('커뮤니티 사용자 검색에 실패하였습니다.')
                .setDescription('인제군 커뮤니티에 가입되어 있는지 다시 한번 확인해주세요!')
                .setColor('Red')
            ],
            components: [],
          });
        }
      } catch (err) {
        console.error(err);
        await interaction.update({
          embeds: [
            new EmbedBuilder()
              .setTitle('오류 발생')
              .setDescription('잠시 후 다시 시도해주세요.')
              .setColor('Red')
          ],
          components: [],
        });
      }
    }
  }

  if (interaction.isModalSubmit()) {
    if (interaction.customId === 'id_modal') {
      const username = interaction.fields.getTextInputValue('roblox_id');

      try {
        const res = await fetch(`https://users.roblox.com/v1/usernames/users`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ usernames: [username] })
        });
        const json = await res.json();
        const robloxId = json.data?.[0]?.id;

        if (!robloxId) throw new Error('ID 변환 실패');

        userRobloxIdMap.set(interaction.user.id, robloxId);

        const embed = new EmbedBuilder()
          .setTitle('다음으로 커뮤니티 가입을 진행해주세요.')
          .setDescription(`[인제군 커뮤니티 링크](https://www.roblox.com/ko/communities/${COMMUNITY_ID}/Ulleung-country#!/about)\n\n커뮤니티에 가입한 후 다음을 눌러주세요.`)
          .setColor('Blue');

        const row = new ActionRowBuilder().addComponents(
          new ButtonBuilder().setCustomId('go_back').setLabel('⬅️이전').setStyle(ButtonStyle.Danger),
          new ButtonBuilder().setCustomId('check_community').setLabel('➡️다음').setStyle(ButtonStyle.Success)
        );

        await interaction.update({ embeds: [embed], components: [row] });
      } catch (e) {
        console.error(e);
        await interaction.reply({
          ephemeral: true,
          embeds: [
            new EmbedBuilder()
              .setTitle('로블록스 사용자 검색 실패')
              .setDescription('정확한 로블록스 ID를 입력했는지 확인해주세요.')
              .setColor('Red')
          ]
        });
      }
    }
  }

  if (interaction.isButton() && interaction.customId === 'open_id_modal') {
    const modal = new ModalBuilder()
      .setCustomId('id_modal')
      .setTitle('로블록스 아이디 입력');

    const idInput = new TextInputBuilder()
      .setCustomId('roblox_id')
      .setLabel('로블록스 아이디를 입력해주세요.')
      .setPlaceholder('예: myRobloxUsername')
      .setStyle(TextInputStyle.Short)
      .setRequired(true);

    const row = new ActionRowBuilder().addComponents(idInput);
    modal.addComponents(row);

    await interaction.showModal(modal);
  }
});

client.login(process.env.TOKEN);
