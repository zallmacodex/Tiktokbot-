const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');

// bot Anda
const token = '7994188138:AAHzCkrbNU94wTqqfWUO-An_n7OLuBpaGSQ';
const bot = new TelegramBot(token, { polling: true });

bot.onText(/\/start/, (msg) => {
    bot.sendMessage(msg.chat.id, "Selamat datang! Kirim URL TikTok untuk memulai.");
});

bot.on('message', async (msg) => {
    const chatId = msg.chat.id;
    const urlRegex = /https:\/\/(www\.)?tiktok\.com\/(@[\w.-]+\/video\/\d+|v[t]\.\w+\/[A-Za-z0-9]+)/;

    if (urlRegex.test(msg.text)) {
        bot.sendMessage(chatId, "Mau download opsi apa? Video atau audio?", {
            reply_markup: {
                inline_keyboard: [
                    [{ text: 'Video', callback_data: 'video' }],
                    [{ text: 'Audio', callback_data: 'audio' }]
                ]
            }
        });

        bot.on('callback_query', async (callbackQuery) => {
            const message = callbackQuery.message;
            const option = callbackQuery.data;

            let apiUrl = `https://bs-api-tiktokv2.vercel.app/tiktok?url=${msg.text}`;

            try {
                const response = await axios.get(apiUrl);
                const { video_url, audio_url } = response.data;

                if (option === 'video') {
                    bot.sendMessage(chatId, "Mengunduh video...");
                    bot.sendVideo(chatId, video_url);
                } else if (option === 'audio') {
                    bot.sendMessage(chatId, "Mengunduh audio...");
                    bot.sendAudio(chatId, audio_url);
                }
            } catch (error) {
                bot.sendMessage(chatId, "Maaf, terjadi kesalahan saat mengunduh. Coba lagi nanti.");
                console.error(error);
            }
        });
    } else {
        bot.sendMessage(chatId, "Tolong kirim URL TikTok yang valid.");
    }
});
