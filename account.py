import os

# import sys

# if len(sys.argv) != 1:
#     print("请输入账号的简写，比如[det3]......")
#     exit(0)
# account = sys.argv[1]
account = 'bet3'
pro_home = __file__[:__file__.rfind("/")]
cur_dir = pro_home + '/account/' + account
for file in os.listdir(cur_dir):
    if file.endswith("ini"):
        os.environ["CONFIG_FILE_PATH"] = os.path.join(cur_dir, file)
    if file.endswith("js"):
        os.environ["TEMPLATE_FILE_PATH"] = os.path.join(cur_dir, file)
