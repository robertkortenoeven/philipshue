
# Daylights.py
#
# Created by Robert Kortenoeven on 02-01-15.
# Copyright (c) 2015. All rights reserved.
#
# Licensed under the BSD License <http://www.opensource.org/licenses/bsd-license>
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
# THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.



## ------------------------------------------------
# Sets light schedules for the day, run early in the morning for desired results

import os
import time
import datetime
from datetime import timedelta
import random
from random import randint

from astral import Astral

from phue import Bridge


# ------------------------------------------------
# some global vars

today = datetime.date.today()
tomorrow = datetime.date.today() + datetime.timedelta(days=1)
rMin = randint(10,55)
bedTime = datetime.time(20, rMin, 32)
sunsetAdjust = 20; #slight adjustment if it tends to get dark earlier
toiletIntervals = 2 #time between visits in hours


# ------------------------------------------------
# Hue section: set the light schedules for the day
b = Bridge('192.168.1.15')
b.connect()
b.get_api()
allLights = b.lights

# Delete all existing schedules
scheds = b.get_schedule()
for i in scheds:
	b.delete_schedule(i)


# ------------------------------------------------
# some helper methods

# offset method to cater for bridge clock being one hour behind (TODO)
def minHour(tm):
    fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
   #fulldate = fulldate + datetime.timedelta(minutes=-60) #add for winter time
    return fulldate.time()

# Debug code setting the time to 10 seconds from now
def addSecs(tm, mins, secs):
    fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    fulldate = fulldate + datetime.timedelta(minutes= mins, seconds=secs)
    return fulldate.time()

# get today's sunset time
def sunsetTimeDate():
	city_name = 'Berlin'
	a = Astral()
	a.solar_depression = 'civil'
	city = a[city_name]
	timezone = city.timezone
	sun = city.sun(date=datetime.date.today(), local=False)
	return str(sun['sunset'] - datetime.timedelta(minutes=sunsetAdjust)) #slight adjustment if it tends to get dark earlier
def bedTimeDate(): #add weekend condition if possible
	timeSched = ('%sT%s' % (str(today),str(bedTime))) #Hue format should be '2015-01-08T14:42:20' 
	return timeSched

def sleepyTime(): #add weekend condition if possible
	sMin = randint(10,55)
	sleeptime = minHour(datetime.time(23, sMin, 59))
	timeSched = ('%sT%s' % (str(today),str(sleeptime))) #Hue format should be '2015-01-08T14:42:20' 
	return timeSched


# -------- SUNSET --------

def setSunsetSchedules(time):
	# Hallway
	data = {'on': True, 'bri': 100, 'transitiontime': 1}
	b.create_schedule('Sunset hallway', time, 1, data, 'Sunset on' )

	# Living room
	data = {'on': True, 'bri': 180, 'transitiontime': 6000}
	b.create_schedule('Sunset living room', time, 3, data, 'Sunset on' )

	# Living room paper lamp
	data = {'on': True, 'bri': 180, 'transitiontime': 6000}
	b.create_schedule('Sunset living room', time, 2, data, 'Sunset on' )

# Get time for sunset and set schedule
sTime = sunsetTimeDate()
sTime = sTime.replace (' ', 'T')
sTime = sTime.replace ('+00:00', '')
print('Sunset today at %s' % str(sTime))
setSunsetSchedules(sTime)


startTimeMorning = datetime.datetime.combine(today, datetime.time(05, 00)) #('%sT05:00:00' % (str(today)))
endTimeEvening = datetime.datetime.combine(tomorrow, datetime.time(01, 00)) #('%sT01:00:00' % (str(tomorrow)))
# toiletsegments = endTime - startTime #total period during which visits occur
visitDuration = randint(10,55)
for startTimeSegment in periodDelta(startTimeMorning, endTimeEvening, timedelta(hours = toiletIntervals)):
	toiletDuration = randint(2,5) #length of visit in minutes
	endTimeSegment = startTimeSegment + datetime.timedelta(hours=+toiletIntervals)
	startVisit = randomDate(startTimeSegment.strftime('%Y-%m-%dT%H:%M:%S'), endTimeSegment.strftime('%Y-%m-%dT%H:%M:%S'), random.random())
	endVisit = datetime.datetime.strptime(startVisit, '%Y-%m-%dT%H:%M:%S') + datetime.timedelta(minutes=+toiletDuration)
	#setBathroomScheduleForPeriod(startVisit,endVisit.strftime('%Y-%m-%dT%H:%M:%S'))
	

# --------- SLEEPY TIME --------
# Generic schedule for turning off all lights after midnight

lightcheck = False
data = {'on': False, 'transitiontime': 1}
for index, light in enumerate(allLights):
	# sInfo = ('Nightime %s' % (str(light))
	b.create_schedule('Nighttime', sleepyTime(), index, data, 'Sleep' )
	if light.reachable == False:
		lightcheck = True

# uncomment these two lines for daily email notifications if one or more lights are switched off (e.g. a friend accidentally turns them off when you're out of the house)
#if (lightcheck == True): #if a light was switched off, send an email
#	os.system("sh /volume1/email_notify.sh")


# -------
# print(b.get_schedule())
print('schedule updated')


