from astrbot.api.all import *
import socket
import astrbot.api.event.filter as event_filter


@register("astrbot_plugin_wol", "Camreishi", "局域网 WOL 唤醒插件，/wolhelp 查看帮助", "1.0.1", 'https://github.com/Camreishi/astrbot_plugin_wol')
class WOLPlugin(Star):
    def __init__(self, context: Context, config: dict = None):
        super().__init__(context)
        self.config = config or {}
        self.target_macs = self.config.get("target_macs", [])
        self.default_mac_address = self.config.get("default_mac_address", "00:00:00:00:00:00")
        self.allowed_sender_ids = self.config.get("allowed_sender_ids", [])
        self.success_message = self.config.get("success_message", "已发送唤醒数据包到 {target_name} ({target_mac})")

    @event_filter.command("wol")
    async def wake_on_lan(self, event: AstrMessageEvent, target: str = None):
        sender_id = event.get_sender_id()

        if self.allowed_sender_ids and sender_id not in self.allowed_sender_ids:
            yield event.plain_result(f"您没有权限使用此命令")
            return

        target_name = "未知设备"  # 初始化 target_name
        target_mac = None  # 初始化 target_mac

        if not target:
            target_mac = self.default_mac_address
            target_name = "默认设备"
        else:
            if ":" in target and len(target.split(":")) == 6:
                # 如果输入的是 MAC 地址
                target_mac = target
                target_name = "通过MAC地址唤醒"
            else:
                # 如果输入的是设备名称
                for item in self.target_macs:
                    parts = item.split(" ", 1)
                    if len(parts) == 2 and parts[0] == target:
                        target_mac = parts[1]
                        target_name = target
                        break

        if not target_mac:
            yield event.plain_result(f"未找到名为 {target} 的目标设备或无效的MAC地址，请检查配置")
            return

        try:
            await self._send_magic_packet(target_mac)
            formatted_message = self.success_message.format(target_name=target_name, target_mac=target_mac)
            yield event.plain_result(formatted_message)

        except Exception as e:
            yield event.plain_result(f"唤醒失败，错误信息: {e}")

    @event_filter.command("wolhelp")
    async def wol_help(self, event: AstrMessageEvent):
        help_message = """
WOL 唤醒插件帮助

命令:
`/wol <设备名称>`: 唤醒指定名称的设备
`/wol <MAC地址>`:  直接使用MAC地址唤醒设备
`/wol`: 唤醒默认设备
`/wolhelp`: 显示此帮助信息

配置:
- `target_macs`: 配置要唤醒的设备列表，格式为 `设备名称 MAC地址`，例如: `pc1 00:11:22:33:44:55`
- `default_mac_address`: 默认目标设备的 MAC 地址
- `success_message`: 自定义唤醒成功后的消息，可以使用 `{target_name}` 和 `{target_mac}` 变量，例如：已发送唤醒数据包到 {target_name} ({target_mac})
- `allowed_sender_ids`: 允许使用命令的发送者 ID 列表，可以通过AstrBot的 `/sid` 命令来获取用户 ID

示例:
`/wol pc1`
`/wol 00:11:22:33:44:55`
`/wol` (使用默认 MAC 地址)
        """
        yield event.plain_result(help_message)

    @staticmethod
    async def _send_magic_packet(mac_address):
        """向指定的MAC地址发送一个魔术包"""
        # 将MAC地址转换为字节
        mac_bytes = bytes.fromhex(mac_address.replace(":", ""))

        # 创建魔术包
        magic_packet = b"\xff" * 6 + mac_bytes * 16

        # 通过UDP广播魔术包
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.sendto(magic_packet, ('<broadcast>', 9))
