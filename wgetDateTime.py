import time, sys

key1 = sys.argv[1]

if key1 == '-h':
  print("HELP:")
  print('Usage - python3 webgrab.py <FILEWITHURLS> <STARTDATE> <TIMETOSTART> <DBFILENAME> <DIRECTORY>')
  print('<FILEWITHURLS> = File that houses urls, one url per line.')
  print('<STARTDATE> = YYYY/MM/DD')
  print('<TIMETOSTART> = HH:MM:SS')
  print('<DBFILENAME> = Name of .db file creates housing all grabbed file names')
  print('<DIRECTORY> = Path to output directory')
  sys.exit()
#establish variables
else :
  urlfile = sys.argv[1]
  startyear, startmonth, startday = sys.argv[2].split('/')
  starthour, startminute, startsecond = sys.argv[3].split(':')
  dbfilename = sys.argv[4]
  directory = sys.argv[5]
  sysyear, sysmon, sysday, syshour, sysmin, syssec = 0,0,0,0,0,0
#find system time
def getTime():
  import datetime
  system_time = datetime.datetime.now()
  sysnow = system_time.strftime("%Y/%m/%d %H:%M:%S")
  sysdate, systime = sysnow.split(' ')
  sysyear, sysmon, sysday = sysdate.split('/')
  syshour, sysmin, syssec = systime.split(':')
  return sysyear, sysmon, sysday, syshour, sysmin, syssec
sysyear, sysmon, sysday, syshour, sysmin, syssec = getTime()
print(f'{sysyear}/{sysmon}/{sysday} {syshour}:{sysmin}:{syssec}')
#write command in log
logfile = open('/var/webgrab/log.txt', 'w+')
logfile.write(f'[{sysyear}/{sysmon}/{sysday} {syshour}:{sysmin}:{syssec}] - python3 webgrab.py {sys.argv[1]} {sys.argv[2]} {sys.argv[3]} {sys.argv[4]} {sys.argv[5]}\n')

#get files
import wget
def getFiles(url):
  try:
    print(f'Gathering {url}')
    file = wget.download(url=url, out=directory)
    sysyear, sysmon, sysday, syshour, sysmin, syssec = getTime()
    logfile.write(f'[{sysyear}/{sysmon}/{sysday} {syshour}:{sysmin}:{syssec}] - Gathered {url}\n')
  except Exception as e:
    print(e)
    sysyear, sysmon, sysday, syshour, sysmin, syssec = getTime()
    logfile.write(f'[{sysyear}/{sysmon}/{sysday} {syshour}:{sysmin}:{syssec}] - {e}\n')

#parse and run through url file
def readUrls():
  urlsfile = open(urlfile, 'r')
  urls = urlsfile.readlines()
  for i in range(len(urls)):
    urls[i] = urls[i].strip()
  print(urls)
  for i in range(len(urls)):
    getFiles(urls[i])

#ping to see if NAS is up
def pingNAS(ip):
  from pythonping import ping
  up = False
  while True:
    response = ping(ip, size=40, count=10)
    if 1000.0 >= float(response.rtt_avg_ms):
      up = True
      break
    else :
      up = False
  return up

#copy files to NAS
def send2NAS(ip):
  import shutil
  sysyear, sysmon, sysday, syshour, sysmin, syssec = getTime()
  logfile.write(f'[{sysyear}/{sysmon}/{sysday} {syshour}:{sysmin}:{syssec}] - Attempting to connect to NAS @ {ip}\n')
  while True:
    if pingNAS(ip) == True:
      break
  sysyear, sysmon, sysday, syshour, sysmin, syssec = getTime()
  logfile.write(f'[{sysyear}/{sysmon}/{sysday} {syshour}:{sysmin}:{syssec}] - Transferring files to {ip}\n')
  filename = f'/nfs/botdata/webGrabber/download-|{startyear}-{startmonth}-{startday}|{starthour}:{startminute}:{startsecond}'
  print(f'Making {filename}...')
  shutil.copytree(f'/home/duncan/downloadedfiles',filename)

#main
if starthour == '--' and startminute == '--' and startsecond == '--':
  sysyear, sysmon, sysday, syshour, sysmin, syssec = getTime()
  starthour, startminute, startsecond = syshour, sysmin, syssec
  readUrls()
else:
  while True:
    sysyear, sysmon, sysday, syshour, sysmin, syssec = getTime()
    print(f'{syshour}:{sysmin}:{syssec} / {starthour}:{startminute}:{startsecond}')
    if int(starthour) == int(syshour) and int(startminute) == int(sysmin) and int(startsecond) == int(syssec) and int(startyear) == int(sysyear) and int(startmonth) == int(sysmon) and int(startday) == int(sysday):
      readUrls()
    else:
      time.sleep(1)
send2NAS('192.168.1.12')
logfile.close()
sys.exit()
