const { createBot } = require('oicq');
const { loadConfig } = require('./config');
const { checkPermission } = require('./permission');
const { startDownload } = require('./downloader');

const bot = createBot(账号)
  .on('message', async (event) => {
    if (!await isJmCommand(event)) return;
    
    try {
      const { albumId, user } = parseCommand(event);
      if (!await checkPermission(event, user)) {
        return event.reply('❌ 权限不足或未正确@机器人');
      }
      
      await event.reply(`⚠️ 确认下载漫画 #${albumId}？(回复 Y 确认)`);
      await handleConfirmation(event, albumId);
    } catch (err) {
      event.reply(`⚠️ 错误: ${err.message}`);
    }
  });

// 命令验证函数
async function isJmCommand(event) {
  const msg = event.raw_message;
  return msg.includes('[CQ:at') && 
         /jm\s+\d+/i.test(msg.replace(/\[CQ:.*?\]/g, ''));
}

// 消息解析函数
function parseCommand(event) {
  const cleanMsg = event.raw_message
    .replace(/\[CQ:at,qq=\d+\]/g, '')
    .trim();
  const albumId = cleanMsg.match(/jm\s+(\d+)/i)?.[1];
  
  if (!albumId) throw new Error('无效的命令格式');
  return { albumId, user: event.user_id };
}

// 确认处理器
async function handleConfirmation(event, albumId) {
  const listener = (confirmEvent) => {
    if (confirmEvent.user_id !== event.user_id) return;
    if (confirmEvent.raw_message.toLowerCase() === 'y') {
      bot.off('message', listener);
      startDownload(albumId, event);
    }
  };
  
  bot.on('message', listener);
  setTimeout(() => bot.off('message', listener), 60000);
}