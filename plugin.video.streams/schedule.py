import xbmc, xbmcgui
import os, os.path, re
import glob
from glob import addon_log, Downloader, message, addon
from datetime import datetime, timedelta
import json

from settings import SETTINGS

try:
  import pytz
  from pytz import timezone
except ImportError as err:
  addon_log( str(err) )
  message(addon.getLocalizedString(30300), str(err) + "\n" + addon.getLocalizedString(30302))

import time
import sys
import sqlite3
#import random

#reload(sys)
#sys.setdefaultencoding('utf-8')

def grab_schedule(id_channel_port, name, force=False, update_all=False):
  addon_log('grab schedule')

  nr_days = 5

  db_connection=sqlite3.connect(SETTINGS.SCHEDULE_PATH)
  db_cursor=db_connection.cursor()

  table_name = name.replace(' ', '_').lower()
  sql = "CREATE TABLE IF NOT EXISTS `%s` (event_time REAL, title TEXT)" % \
        (table_name)
  db_cursor.execute(sql);

  now_utc = datetime.now(timezone('UTC'))
  tz_ro = timezone('Europe/Bucharest')
  dt_ro = tz_ro.normalize(now_utc.astimezone(tz_ro))

  if force == False:
    sql="SELECT event_time FROM `%s` ORDER BY event_time ASC LIMIT 1" % \
        (table_name)
    db_cursor.execute(sql)
    rec = db_cursor.fetchone()
    if rec:
      #addon_log(rec[0]);
      #addon_log(time.mktime(dt_ro.timetuple()));
      if ((time.mktime(dt_ro.timetuple()) - rec[0]) < (60*60*24*2)): #update only if schedule is older than 2 days
        addon_log('schedule is up to date')
        if update_all:
          xbmc.executebuiltin("Notification(%s,%s,%i)" % (name, addon.getLocalizedString(30056), 1000))  #Schedule is up to date
        return True

  addon_log('update schedule')

  month_name_to_no={"Ianuarie" : "01",
                    "Februarie" : "02",
                    "Martie" : "03",
                    "Aprilie" : "04",
                    "Mai" : "05",
                    "Iunie" : "06",
                    "Iulie" : "07",
                    "August" : "08",
                    "Septembrie" : "09",
                    "Octombrie" : "10",
                    "Noiembrie" : "11",
                    "Decembrie" : "12"}

  #event_year = dt_ro.year
  start_date=dt_ro
  end_date = start_date + timedelta(days=nr_days)
  #end_date = start_date
  #url="http://port.ro/pls/w/tv.channel?i_xday="+str(nr_days)+"&i_date=%i-%02i-%02i&i_ch=%s" % (start_date.year , start_date.month , start_date.day , id_channel_port)
  
  i_datetime_from = start_date.strftime('%Y-%m-%d')
  i_datetime_to = end_date.strftime('%Y-%m-%d')
  url="http://port.ro/pls/w/tv_api.event_list?i_channel_id=%s&i_datetime_from=%s&i_datetime_to=%s" % (id_channel_port, i_datetime_from, i_datetime_to)
  #addon_log(url)

  temp = os.path.join(SETTINGS.ADDON_PATH,"temp.htm")
  try:
    Downloader(url, temp, addon.getLocalizedString(30061), addon.getLocalizedString(30062) + " " + name)  #Downloading Schedule
    f = open(temp)
    schedule_txt = f.read()
    f.close()
    os.remove(temp)
  except Exception as inst:
    schedule_txt = ""

  #addon_log(schedule_txt)
  try:
    schedule_json = json.loads(schedule_txt, encoding='iso-8859-2')
  except Exception as inst:
    db_connection.commit()
    db_connection.close()
    return False
  
  sql="DELETE FROM `%s`" % \
       (table_name)
  db_cursor.execute(sql)
    
  for k in schedule_json: #for every day
    for program in schedule_json[k]['channels'][0]["programs"]: #every program in a day
      event_title = program['title']
      start_datetime = re.sub('[\+-]+\d+:\d+$', '', program['start_datetime'])
      event_timestamp = time.mktime(time.strptime(start_datetime, "%Y-%m-%dT%H:%M:%S"))
      sql="INSERT INTO `%s` VALUES (?, ?)" % \
           (table_name)
      #st = db_cursor.execute(sql, (event_timestamp, unicode(event_title.replace("'", ""), 'iso-8859-2')))
      st = db_cursor.execute(sql, (event_timestamp, event_title))

  # match=re.compile(r'class="begin_time">(?P<time>.*?)</p>').search(schedule_txt)
  # if match:
  #   now_time=match.group('time')
  # else:
  #   now_time=""
  # #addon_log(now_time)
  # 
  # next_year = None
  # 
  # match_days=re.compile('<td style="vertical-align:top;text-align:center">\n*\s*<p class="date_box" style="margin-bottom:0px">\n*\s*<span>\n(?P<date>.*?)\n*\s*</span><br/>(?P<content>.*?)\n*\s*</table>\n*\s*</td>',re.DOTALL).findall(schedule_txt)
  # if match_days:
  #   i=1
  #   prev_event_day = None
  #   prev_event_month = None
  #   for date,content in match_days:
  #     date_obj = re.match( '.*? \((.*) (.*)\)', date)
  # 
  #     event_day=date_obj.group(1).zfill(2)
  #     event_month=month_name_to_no[date_obj.group(2)]
  #     event_year = dt_ro.year
  # 
  #     if (event_day == '01') and (event_month == '01') and (((i > 1) and (i < nr_days)) or (i > nr_days + 1)):
  #       next_year = event_year+1
  #     elif i == (nr_days + 1):
  #       next_year = None
  # 
  #     if next_year != None :
  #       event_year = next_year
  # 
  #     #addon_log(event_day + " " + event_month)
  # 
  #     if content:
  #       match_events_re=re.compile('btxt\" style=\"width:40px;margin:0px;padding:0px\">(?P<event_time>.*?)<.*?btxt\">(?P<event_title>.*?)</(?P<event_details>.*?)</td></tr>',re.DOTALL)
  #       match_events = match_events_re.findall(content)
  #     else:
  #       return False
  # 
  #     prev_event_hour = None
  #     if match_events:
  #       for event_time , event_title , event_details in match_events:
  #         if event_time == '':
  #           event_time=now_time
  # 
  #         event_hour=event_time.split(":")[0].zfill(2)
  #         event_minutes=event_time.split(":")[1]
  # 
  #         if (event_hour < prev_event_hour): #what is after midnight is moved to the next day
  #           next_day = datetime(int(event_year), int(event_month), int(event_day)) + timedelta(days = 1)
  #           #addon_log(next_day)
  #           prev_event_day = event_day
  #           prev_event_month = event_month
  #           event_day = next_day.strftime('%d')
  #           event_month = next_day.strftime('%m')
  # 
  # 
  #         #addon_log(event_day+" "+event_month+" "+str(prev_event_day)+" "+str(prev_event_month))
  #         if (event_day == '01') and (event_month == '01') and (prev_event_day == '31') and (prev_event_month=='12') and (event_year == dt_ro.year):
  #           event_year += 1
  #           prev_event_day = None
  #           prev_event_month = None
  # 
  #         event_timestamp = time.mktime(time.strptime(event_day+"-"+event_month+"-"+str(event_year)+" "+event_hour+":"+event_minutes, "%d-%m-%Y %H:%M"))
  # 
  #         #addon_log(event_time)
  #         #addon_log(event_day+" "+event_month+" "+str(event_year)+" "+event_hour+":"+event_minutes + " " + event_title)
  #         #addon_log(event_time + "  " + str(event_timestamp) + " " + event_title)
  # 
  #         sql="INSERT INTO `%s` VALUES (?, ?)" % \
  #              (table_name)
  #         st = db_cursor.execute(sql, (event_timestamp, unicode(event_title.replace("'", ""), 'iso-8859-2')))
  #         #addon_log(sql)
  # 
  #         prev_event_hour = event_hour
  # 
  #     prev_event_day = event_day
  #     prev_event_month = event_month
  # 
  #     i+=1

  db_connection.commit()
  db_connection.close()
  #xbmc.sleep(random.randint(500, 2000)) #random delay for scraping

def load_schedule(name):
  addon_log('load schedule ' + name)
  schedule = []

  db_connection=sqlite3.connect(SETTINGS.SCHEDULE_PATH)
  db_cursor=db_connection.cursor()

  table_name = name.replace(' ', '_').lower()

  now_utc = datetime.now(timezone('UTC'))
  tz_ro = timezone('Europe/Bucharest')
  dt_ro = tz_ro.normalize(now_utc.astimezone(tz_ro))

  try:
    active_event = load_active_event(name)
    if active_event:
      schedule.append(active_event)

    sql="SELECT event_time, title FROM `%s` WHERE event_time > ? ORDER BY event_time ASC LIMIT 10" % \
         (table_name,)
    #addon_log(sql)
    db_cursor.execute(sql, (time.mktime(dt_ro.timetuple()),) )
    rec=db_cursor.fetchall()

    if len(rec)>0:
      for event_time, title in rec:
        event = add_event(event_time, title)
        schedule.append(event)

  except Exception as inst:
    #addon_log(inst)
    pass

  if len(schedule)>=2:
    schedule_txt = ' - '.join(schedule)
  else:
    schedule_txt = '( [I]'+addon.getLocalizedString(30064)+'[/I] )'
  #addon_log(schedule_txt)

  return schedule_txt

def load_active_event(name):
  db_connection=sqlite3.connect(SETTINGS.SCHEDULE_PATH)
  db_cursor=db_connection.cursor()

  table_name = name.replace(' ', '_').lower()

  now_utc = datetime.now(timezone('UTC'))
  tz_ro = timezone('Europe/Bucharest')
  dt_ro = tz_ro.normalize(now_utc.astimezone(tz_ro))

  event = None

  try:
    sql="SELECT event_time, title FROM `%s` WHERE event_time <= ? ORDER BY event_time DESC LIMIT 1" % \
        (table_name,)
    db_cursor.execute(sql, ( time.mktime(dt_ro.timetuple()), ) )
    rec=db_cursor.fetchone()
    if rec:
      event = add_event(rec[0], rec[1])
      schedule.append(event)
  except: pass

  #addon_log(event)

  return event

def add_event(event_time, title):
  tz_offset = float(time.strftime('%z'))/100  #xbmc offset
  #addon_log(tz_offset)

  tz_ro = timezone('Europe/Bucharest')
  now_ro = datetime.now(tz_ro)
  tz_ro_offset = float(now_ro.strftime('%z'))/100  #port.ro offset

  dt_ro = datetime.fromtimestamp(event_time)
  dt_display = dt_ro - timedelta(hours = tz_ro_offset) + timedelta(hours = tz_offset)

  #addon_log(dt_display.strftime('%H:%M') + " " + title)
  #addon_log(dt_display)
  #addon_log(dt_ro.strftime('%H:%M') + " " + title)
  #addon_log(event_time)
  #addon_log(dt_ro)
  #addon_log(title)

  event = dt_display.strftime('%H:%M') + " " + title
  return event
