import datetime
import glob
import gzip
import os
import subprocess
import sys
import time
from io import BytesIO
import requests
import pycurl
from cursesmenu import *
from cursesmenu.items import *

def getlists(last_updated):
	url = "https://malshare.com/daily/"
	date = datetime.datetime(int(last_updated[0].split("-")[0]), int(last_updated[0].split("-")[1]), int(last_updated[0].split("-")[2]))
	sdate = str(date)
	sdate, space, time = sdate.partition(" ")
	date_to_replace = sdate
	hashes = "/malshare_fileList"
	while (sdate != str(datetime.datetime.today()).split()[0]):
		if (datetime.datetime.strptime(sdate, '%Y-%m-%d') > datetime.datetime(2017, 9, 14)):
			newurl = url + sdate + hashes + "." + sdate + ".txt"
		else:
			newurl = url + "/_disabled/" + sdate + hashes + "." + sdate + ".txt"
		print(newurl)
		c = pycurl.Curl()
		buff = BytesIO()
		c.setopt(c.URL, newurl)
		d = subprocess.check_output('sudo docker ps', shell=True)
		if (d.find('torproxy') != -1) and (d.find('privoxy') != -1):
			c.setopt(pycurl.PROXY, 'localhost')
			c.setopt(pycurl.PROXYPORT, 9050)
			c.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)
		c.setopt(c.WRITEDATA, buff)
		c.perform()
		body = buff.getvalue()
		if "404 Not Found" not in body:
			with open("hashes/" + sdate + ".txt", "w") as fi:
				fi.write(body)
		date += datetime.timedelta(days=1)
		sdate = str(date)
		sdate, space, time = sdate.partition(" ")
	f = open("config.cfg", "r")
	filecon = f.readlines()
	f.close()
	f = open("config.cfg", "w")
	filecon[0] = filecon[0].replace(date_to_replace.split()[0], str(datetime.datetime.today()).split()[0])
	f.writelines(filecon)
	f.close()


def getfiles(h, writefolder, api):
	h = h.split("\n")[0]
	if "tmp/" in h:
		h = h.split("/")[3]
	if " " in h:
		h = h.split(" ")[0]
	try:
		malshare_url = "http://api.malshare.com/sampleshare.php"
		payload = {'action': 'getfile', 'api_key': api, 'hash': h}
		user_agent = {'User-agent': 'malshare'}
		proxydict = {"http": None}
		d = subprocess.check_output('sudo docker ps', shell=True)
		if (d.find('torproxy') != -1) and (d.find('privoxy') != -1):
			proxydict.update = {"http": "localhost:8118"}
		r = requests.get(malshare_url, params=payload, headers=user_agent, proxies=proxydict)
		sample = r.content
		with gzip.open(writefolder+"/" + h + ".gz", "wb") as f:
			f.write(sample)
		print h
	except:
		print("Error! File not downloaded.")


def updateDB(arg):
	list_files = glob.glob("hashes/*.txt")
	f = open("config.cfg", "r")
	filecon = f.readlines()
	f.close()
	apiKeys = (filecon[1].split("keys:")[1]).split(":")
	api_count = filecon[2].split(":")[1]
	t = filecon[3].split(":")[1]
	for i in list_files:
		to_open = i.split("/")[1]
		fi = open(i)
		to_download = fi.readlines()
		a = i.split("/")
		a[0] = "files"
		st = "/".join(a)
		st = st.split(".txt")[0]
		if not os.path.exists(st):
			os.mkdir(st)
		for j in to_download:
			getfiles(j, st, apiKeys[t].split("\n")[0])
			api_count = str(int(api_count) + 1)
			f = open("config.cfg", "w")
			filecon[2] = filecon[2].replace(filecon[2].split(":")[1], api_count)
			f.writelines(filecon)
			f.close()
			if int(api_count) >= 1000:
				f = open("config.cfg", "w")
				filecon[2] = filecon[2].replace(filecon[2].split(":")[1], "0")
				f.writelines(filecon)
				f.close()
				if int(t) < len(apiKeys):
					t = str(int(t) + 1)
					f = open("config.cfg", "w")
					filecon[3] = filecon[3].replace(filecon[3].split(":")[1], t)
					f.writelines(filecon)
					f.close()
				else:
					print "You have exceeded file download limit!"
					sys.exit(0)
		fi.close()


def enableProxy():
	d = subprocess.check_output('sudo docker ps -a', shell=True)
	if (d.find('torproxy') == -1):
		subprocess.call("sudo docker run -d --restart always -v /etc/localtime:/etc/localtime:ro -p 9050:9050 --name torproxy jess/tor-proxy", shell=True)
	if (d.find('privoxy') == -1):
		subprocess.call("sudo docker run -d --restart always -v /etc/localtime:/etc/localtime:ro --link torproxy:torproxy -p 8118:8118 --name privoxy jess/privoxy", shell=True)
    
	if (d.find('torproxy') != -1):
		subprocess.call("sudo docker start torproxy", shell=True)
	if (d.find('privoxy') != -1):
		subprocess.call("sudo docker start privoxy", shell=True)
	time.sleep(1)


def disableProxy():
	d = subprocess.check_output('sudo docker ps', shell=True)
	if (d.find('torproxy') != -1):
		subprocess.call("sudo docker stop torproxy", shell=True)
	if (d.find('privoxy') != -1):
		subprocess.call("sudo docker stop privoxy", shell=True)
	time.sleep(1)


def checkProxy():
	d = subprocess.check_output('sudo docker ps', shell=True)
	if (d.find('torproxy') != -1) and (d.find('privoxy') != -1):
		print("Proxy is on")
	else:
		print("Proxy is off")
	time.sleep(1)


def main():
	menu = CursesMenu("Malware Updater from malshare website","Select from below:")
	lines = [line.rstrip('\n') for line in open('config.cfg')]
	selection_menu = SelectionMenu(lines[1].split(":")[1:])
	function_item1 = FunctionItem("Update the signature list", getlists, args=[lines[0].split(":")[1:]], should_exit=False)
	function_item2 = FunctionItem("Update the database", updateDB, args=["Updating the database"], should_exit=False)
	function_item3 = FunctionItem("Enable Proxy", enableProxy, args=[], should_exit=False)
	function_item4 = FunctionItem("Disable Proxy", disableProxy, args=[], should_exit=False)
	function_item5 = FunctionItem("Check Proxy", checkProxy, args=[], should_exit=False)
	menu.append_item(function_item1)
	menu.append_item(function_item2)
	menu.append_item(function_item3)
	menu.append_item(function_item4)
	menu.append_item(function_item5)
	menu.show()


if __name__ == '__main__':
	main()

			
			
			