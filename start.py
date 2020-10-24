import pexpect
from hurry.filesize import size
import os
import platform
import sys
import random
import time
import math
import psutil
import yaml
import shutil
from mega import Mega
import zipfile
try:
    with open('conf.yml') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
except:
    data = {'lang': 'en', 'world_size': 2000, 'world_name': 'world', 'ram_size': 1024, 'server_dir': os.getcwd(), 'pushbullet': {'enabled': False, 'token': ' ', 'device': ' '}}
    with open('conf.yml', 'w') as f:
        yaml.dump(data, f)
    print("Config file created! Please configure it now.")
    exit()
try:
    os.chdir('languages')
    with open(data['lang'] + ".yml") as f:
        lng = yaml.load(f, Loader=yaml.FullLoader)
except:
    print('Lang file "{}.yml" not found!'.format(data['lang']))
    exit()
rozm = data['world_size']
swi = data['world_name']
ram = data['ram_size']
lok = data['server_dir']
notif = data['pushbullet']
if notif['enabled']:
    from pushbullet import Pushbullet
    pb = Pushbullet(notif['token'])
    dev = pb.get_device(notif['device'])
    pbttl = lng['pushbullet_title']
print("{}: {}".format(lng['size'], rozm))
print("{}: {}".format(lng['name'], swi))
print("{}: {}".format(lng['maxram'], ram))
print("{}: {}".format(lng['srvloc'], lok))
if not os.path.exists(lok + "/wgen"):
    print(lng['downloading'])
    if not os.path.exists(lok):
        os.mkdir(lok)
    os.chdir(lok)
    mega = Mega().login()
    mega.download_url("https://mega.nz/file/fNxUkDpa#XW22WLpg7yzShExpNsIdrmfcxNMyk1Gl_vWA8hUeDT4")
    print(lng['unpacking'])
    with zipfile.ZipFile("wgen.zip", "r") as zip_ref:
        zip_ref.extractall(lok)
os.chdir(lok + "/wgen")
print(lng['starting'])
srv = pexpect.spawn("java -Xmx{}M -Xms{}M -jar srv.jar".format(ram, ram))
srv.expect('For help, type', timeout=120)
print(lng['started'])
srv.sendline("mw create {}".format(swi))
srv.sendline("mw load {}".format(swi))
srv.expect(["CONSOLE: World {} loaded succesfully!".format(swi), "World {} is already loaded, no need to load it again!".format(swi)], timeout=None)
print(lng['loaded'])
srv.sendline("wb fill cancel")
srv.sendline("wb {} set {} 0 0".format(swi, rozm))
srv.sendline("wb {} fill".format(swi))
srv.sendline("wb fill confirm")
srv.expect('WorldBorder map generation task for world "{}" started.'.format(swi))
print(lng['generating'])
if notif['enabled']:
    dev.push_note(pbttl, lng['generating'])
prevchks = 0
frame = ""
for i in range(20):
    frame = frame + random.choice(["*","^"])
try:
    while True:
        rt = srv.expect(["more chunks processed ","task successfully completed for world"])
        if rt == 0:
            if platform.system == "Windows":
                os.system("cls")
            else:
                os.system("clear")
            parsed = str(srv.readline()).replace("\\r\\n'", "").replace("b'", "").replace("(", "")
            parsed = parsed.replace(")", "").split(" ")
            frame = ""
            for i in range(20):
                frame = frame + random.choice(["*","^"])
            print(frame)
            print("{}: {} (+{})".format(lng['total'], parsed[0], int(parsed[0]) - prevchks))
            print("{}: {}B".format(lng['mem'], size(int(parsed[5]) * 1024 * 1024)))
            print("{}: {}".format(lng['progress'], parsed[2]))
            print("{}: ".format(lng['temperature']) + str(math.floor(psutil.sensors_temperatures()['cpu_thermal'][0].current)) + "C")
            print("{}: ".format(lng['cpufreq']) + str(math.floor(psutil.cpu_freq().current)) + "MHz")
            print(frame)
            prevchks = int(parsed[0])
        else:
            print(lng['finished'])
            if notif['enabled']:
                dev.push_note(pbttl, lng['finished'])
            break
except KeyboardInterrupt:
    pass
print(lng['stopping'])
srv.sendline("stop")
srv.expect(pexpect.EOF)
