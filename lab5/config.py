import os

# Reddit API credentials (set these in Colab before running pipeline)
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "VmaxrRGD52J_iJ0vJ0nR6A")
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "2_-M2bL6IdjUFsojNuyS08I5gqKHNQ")
REDDIT_USER_AGENT = os.environ.get("REDDIT_USER_AGENT", "colab:DSCI-560:1.0 (by u/Historical-Ladder929)")

# MySQL credentials
MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "root")
MYSQL_DB = os.environ.get("MYSQL_DB", "reddit_dsci560")
