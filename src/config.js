const fs = require('fs/promises');
const path = require('path');

const defaultConfig = {
  savePath: "./downloads",
  proxy: "",
  allowGroups: [],
  maxConcurrent: 3
};

async function loadConfig() {
  const configPath = path.join(__dirname, '../config/jmcomic.json');
  
  try {
    const data = await fs.readFile(configPath, 'utf8');
    return { ...defaultConfig, ...JSON.parse(data) };
  } catch (err) {
    await fs.writeFile(configPath, JSON.stringify(defaultConfig, null, 2));
    return defaultConfig;
  }
}

module.exports = { loadConfig };