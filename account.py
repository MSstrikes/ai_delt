import os
import sys

if len(sys.argv) != 2:
    print("请输入账号的简写，比如[bet3]......")
    exit(0)
account = sys.argv[1]
pro_home = __file__[:__file__.rfind("/")]
cur_dir = pro_home + '/account/' + account
for file in os.listdir(cur_dir):
    if file.endswith("ini"):
        os.environ["CONFIG_FILE_PATH"] = os.path.join(cur_dir, file)
    if file.endswith("js"):
        os.environ["TEMPLATE_FILE_PATH"] = os.path.join(cur_dir, file)
