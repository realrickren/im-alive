#!/bin/bash
exec 1>> /tmp/imalive.log 2>&1
echo "=== Script started at $(date) ==="
cd /Users/qinze/workspace/product/im-alive  # 你的实际路径
echo "Current directory: $(pwd)"
echo "Running as user: $(whoami)"
/Users/qinze/.pyenv/versions/3.10.0/bin/python pc-client.py  # 你的 Python 路径
echo "=== Script finished at $(date) ==="
