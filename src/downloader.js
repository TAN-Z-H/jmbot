const { spawn } = require('child_process');
const path = require('path');
const { loadConfig } = require('./config');

const activeDownloads = new Map();

async function startDownload(albumId, event) {
  const config = await loadConfig();
  
  if (activeDownloads.has(albumId)) {
    return event.reply('⚠️ 该漫画正在下载中');
  }
  
  const downloader = spawn('python', [
    '-m', 'jmcomic',
    'download', albumId,
    '--output', path.join(config.savePath, albumId),
    '--proxy', config.proxy || ''
  ]);
  
  activeDownloads.set(albumId, downloader);
  
  downloader.stdout.on('data', (data) => {
    const progress = parseProgress(data.toString());
    if (progress) event.reply(`进度: ${progress}%`);
  });
  
  downloader.on('close', (code) => {
    activeDownloads.delete(albumId);
    event.reply(code === 0 
      ? `✅ 下载完成！路径: ${path.join(config.savePath, albumId)}`
      : '⚠️ 下载失败');
  });
}

function parseProgress(output) {
  const match = output.match(/Progress: (\d+)%/);
  return match ? match[1] : null;
}

module.exports = { startDownload };