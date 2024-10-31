import os
from datetime import datetime, timedelta
import json
from github import Github

class MobileAliveSignal:
    def __init__(self, config_path="config.json"):
        with open(config_path) as f:
            self.config = json.load(f)
        self.github = Github(self.config["github_token"])
        # 获取两个仓库
        self.im_alive_repo = self.github.get_repo(self.config["repo_name"])
        self.profile_repo = self.github.get_repo(f"{self.config['github_username']}/{self.config['github_username']}")

    def update_readmes(self):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            update_line = f"📱 Mobile Update: {timestamp} via SSH Auto Check"

            # 更新 im-alive 仓库
            self.update_repo_readme(self.im_alive_repo, update_line)

            # 更新个人资料仓库
            self.update_repo_readme(self.profile_repo, update_line)

            print(f"Successfully updated both repos at {timestamp}")

        except Exception as e:
            print(f"Error updating READMEs: {str(e)}")

    def update_repo_readme(self, repo, update_line):
        try:
            contents = repo.get_contents("README.md")
            current_content = contents.decoded_content.decode()
            new_content = self.update_content_section(current_content, update_line)

            repo.update_file(
                "README.md",
                f"Mobile Update {datetime.now().strftime('%Y-%m-%d')}",
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

def should_update():
    last_update_file = "last_mobile_update.txt"
    now = datetime.now()

    # 检查上次更新时间
    # if os.path.exists(last_update_file):
    #     with open(last_update_file, 'r') as f:
    #         last_update = datetime.fromisoformat(f.read().strip())
    #         # 如果距离上次更新不足24小时，跳过
    #         if now - last_update < timedelta(hours=24):
    #             return False

    # 记录本次更新时间
    with open(last_update_file, 'w') as f:
        f.write(now.isoformat())
    return True

if __name__ == "__main__":
    if should_update():
        signal = MobileAliveSignal()
        signal.update_readmes()
    else:
        print("Skipped: Last update was too recent")
