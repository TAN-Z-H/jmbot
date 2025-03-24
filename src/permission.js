const superAdmins = new Set(['管理员QQ号']);

async function checkPermission(event, user) {
  // 私聊直接允许
  if (event.message_type === 'private') return true;
  
  // 群组白名单检查
  const config = await loadConfig();
  const inWhitelist = config.allowGroups.includes(event.group_id);
  
  // 管理员权限检查
  const isAdmin = await checkGroupAdmin(event);
  
  return superAdmins.has(user) || (inWhitelist && isAdmin);
}

async function checkGroupAdmin(event) {
  const info = await bot.getGroupMemberInfo(event.group_id, event.user_id);
  return info.role === 'admin' || info.role === 'owner';
}

module.exports = { checkPermission };