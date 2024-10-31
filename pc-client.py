# pc_client.py

import os
from datetime import datetime
import json
import requests
from github import Github
import platform
import socket

class PCAliveSignal:
    def __init__(self, config_path="config.json"):
        self.load_config(config_path)
        self.github = Github(self.config["github_token"])
        # 获取两个仓库
        self.im_alive_repo = self.github.get_repo(self.config["repo_name"])
        self.profile_repo = self.github.get_repo(f"{self.config['github_username']}/{self.config['github_username']}")

    def load_config(self, config_path):
        if not os.path.exists(config_path):
            self.initial_setup(config_path)
        with open(config_path) as f:
            self.config = json.load(f)

    def initial_setup(self, config_path):
        config = {
            "github_token": input("输入GitHub令牌: "),
            "repo_name": input("输入仓库名 (格式: username/repo): "),
            "github_username": input("输入GitHub用户名: "),
            "telegram_bot_token": input("输入Telegram Bot令牌: "),
            "chat_id": input("输入Telegram聊天ID: ")
        }
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

    def get_system_info(self):
        return {
            "platform": platform.system(),
            "hostname": socket.gethostname(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def update_readmes(self):
        try:
            system_info = self.get_system_info()
            update_line = f"🖥️ PC Update: {system_info['timestamp']} from {system_info['hostname']} ({system_info['platform']})"

            # 更新 im-alive 仓库
            self.update_repo_readme(self.im_alive_repo, update_line)

            # 更新个人资料仓库
            self.update_repo_readme(self.profile_repo, update_line)

            print(f"Successfully updated both repos at {datetime.now()}")
            self.send_telegram_notification("PC更新成功！")

        except Exception as e:
            print(f"Error updating READMEs: {str(e)}")

    def update_repo_readme(self, repo, update_line):
        try:
            contents = repo.get_contents("README.md")
            current_content = contents.decoded_content.decode()
            new_content = self.update_content_section(current_content, update_line)

            repo.update_file(
                "README.md",
                f"PC Update {datetime.now().strftime('%Y-%m-%d')}",
                new_content,
                contents.sha
            )
        except Exception as e:
            print(f"Error updating {repo.name}: {str(e)}")

    def update_content_section(self, content, update_line):
        """智能更新README内容，只保留最新的一条PC更新和一条Mobile更新"""
        lines = content.split('\n')
        new_lines = []
        update_section = False
        pc_update = None
        mobile_update = None

        # 先找到最新的PC和Mobile更新
        for line in lines:
            if update_section and line.strip():
                if 'PC Update:' in line and not pc_update:
                    pc_update = line
                elif 'Mobile Update:' in line and not mobile_update:
                    mobile_update = line
            if line.startswith("## 最近更新"):
                update_section = True
            elif update_section and line.startswith('#'):
                update_section = False

        # 重新构建内容
        update_section = False
        for line in lines:
            if line.startswith("## 最近更新"):
                update_section = True
                new_lines.append(line)
                new_lines.append("")  # 添加空行
                new_lines.append(update_line)  # 添加新的更新
                # 添加之前的更新（如果存在）
                if 'PC Update:' in update_line:
                    if mobile_update:  # 如果是PC更新，保留最新的Mobile更新
                        new_lines.append("")  # 添加空行
                        new_lines.append(mobile_update)
                elif 'Mobile Update:' in update_line:
                    if pc_update:  # 如果是Mobile更新，保留最新的PC更新
                        new_lines.append("")  # 添加空行
                        new_lines.append(pc_update)
                continue

            if update_section and line.startswith('#'):
                update_section = False

            if not update_section:
                new_lines.append(line)

        if not update_section:  # 如果没找到更新部分，创建一个
            new_lines.extend([
                "\n## 最近更新",
                "",  # 添加空行
                update_line
            ])

        return '\n'.join(new_lines)

    def send_telegram_notification(self, message):
        """发送Telegram通知"""
        url = f"https://api.telegram.org/bot{self.config['telegram_bot_token']}/sendMessage"
        data = {
            "chat_id": self.config['chat_id'],
            "text": message
        }
        try:
            requests.post(url, json=data)
        except Exception as e:
            print(f"Error sending Telegram notification: {str(e)}")

if __name__ == "__main__":
    signal = PCAliveSignal()
    signal.update_readmes()
