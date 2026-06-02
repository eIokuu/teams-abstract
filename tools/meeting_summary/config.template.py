"""
会议摘要分析工具 - 配置文件
复制为 config.py 并填写你的 API Key
"""

# ===================== API 配置 =====================
LLM_API_KEY = "sk-your-api-key-here"
LLM_BASE_URL = "https://api.openai.com/v1"
LLM_MODEL = "gpt-4o"

# ===================== 输入/输出路径 =====================
WATCH_FOLDER = r"E:\sam3-main\tools\meeting_summary\transcripts\inbox"
ARCHIVE_FOLDER = r"E:\sam3-main\tools\meeting_summary\transcripts\archive"
OUTPUT_FOLDER = r"E:\sam3-main\tools\meeting_summary\output"

# ===================== 处理选项 =====================
TRANSCRIPT_ENCODING = "utf-8"
OUTPUT_FORMAT = "md"
