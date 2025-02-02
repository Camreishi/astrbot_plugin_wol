from astrbot.api.all import *
import socket
import astrbot.api.event.filter as event_filter


@register("astrbot_plugin_wol", "Camreishi", "局域网 WOL 唤醒插件", "1.0.0", 'https://github.com/Camreishi/astrbot_plugin_wol')
class WOLPlugin(Star):
    def __init__(self, context: Context, config: dict = None):
        super().__init__(context)
        self.config = config or {}
        self.target_macs = self.config.get("target_macs", [])  # 修改为列表
        self.default_mac_address = self.config.get("default_mac_address", "00:00:00:00:00:00")
        self.allowed_sender_ids = self.config.get("allowed_sender_ids", [])
        self.success_message = self.config.get("success_message", "已发送唤醒数据包到 {target_name} ({target_mac})。")

    @event_filter.command("wol")
    async def wake_on_lan(self, event: AstrMessageEvent, target_name: str = None):
        sender_id = event.get_sender_id()

        if self.allowed_sender_ids and sender_id not in self.allowed_sender_ids:
            yield event.plain_result(f"您没有权限使用此命令。")
            return

        if not target_name:
            target_mac = self.default_mac_address
            target_name = "默认设备"
        else:
            target_mac = None  # 初始化 target_mac
            for item in self.target_macs:
                parts = item.split(" ", 1)  # Split into name and mac
                if len(parts) == 2 and parts[0] == target_name:
                    target_mac = parts[1]
                    break

            if not target_mac:
                yield event.plain_result(f"未找到名为 {target_name} 的目标设备，请检查配置。")
                return

        try:
            await self._send_magic_packet(target_mac)
            formatted_message = self.success_message.format(target_name=target_name, target_mac=target_mac)
            yield event.plain_result(formatted_message)

        except Exception as e:
            yield event.plain_result(f"唤醒失败，错误信息: {e}")

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
