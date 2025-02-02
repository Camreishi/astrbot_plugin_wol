# astrbot_plugin_wol

## 简介

适用于 AstrBot 的 Wake-on-LAN (WOL) 插件，帮助用户通过聊天命令唤醒局域网内的计算机或其他支持 WOL 的设备。

## 功能

*   **远程唤醒：** 发送 WOL 魔术包到指定的 MAC 地址，唤醒局域网内的设备。
*   **可配置目标设备：** 可以配置多个目标设备及其对应的 MAC 地址。
*   **默认 MAC 地址：** 可以设置一个默认的 MAC 地址，用于唤醒未指定名称的设备。
*   **自定义成功消息：** 可以自定义成功发送唤醒数据包后的消息，可以使用变量 `{target_name}` 和 `{target_mac}`。
*   **发送者权限控制：** 可以限制只有指定的发送者 ID 才能使用该命令，增强安全性。

## 注意

*   确保你的目标设备已启用 WOL。
*   确保配置的 MAC 地址正确。
*   确保 `allowed_sender_ids` 中的 ID 是正确的用户 ID，你可以通过AstrBot的 `/sid` 命令来获取用户 ID。
*   插件发送的魔术包是广播到本地网络的，因此需要设备和 AstrBot 在同一局域网内。

## 作者

*   Camreishi

## 版本

*   1.0.0

## 许可

GNU Affero General Public License v3.0