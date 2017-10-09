#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import re
from django.utils import simplejson
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
	
class Channel(db.Model):
	network = db.StringProperty() # FOX
	virtual = db.StringProperty() # 13-1
	callsign = db.StringProperty() # KCPQ
	latlon = db.GeoPtProperty()	# 47.7,-122.4


class MainHandler(webapp.RequestHandler):
    def get(self):
		template_values = {
			"app_name": "What Channel is the Game On",
			"ip": "",
			"latlng": "",
			"zip": "",
			"virtual": ""
		}
		
		# todo:
		#  use wget api from csspalette to get hostip.info xml
		#  parse xml
		#  ask google api for place
		#  write to template
		# http://api.hostip.info/?ip=
		# http://www.geobytes.com/IpLocator.htm?GetLocation&template=json.txt&ipaddress=203.30.195.10
		# http://www.fcc.gov/cgi-bin/maps/coverage.pl?startpoint=
		
		template_values["ip"] = self.request.remote_addr
		# template_values["ip"] = "24.22.211.139"
		# template_values["ip"] = "216.163.72.2"
		# template_values["ip"] = "72.167.250.60"
		
		template_values["virtual"] = self.request.get("v")
		
		# result = urlfetch.fetch("http://www.geobytes.com/IpLocator.htm?GetLocation&template=json.txt&ipaddress=" + template_values["ip"])
		# 	if result.status_code == 200:
		# 		location = simplejson.loads(result.content)
		# 		template_values["latlng"] = str(location["geobytes"]["latitude"]) + "," + str(location["geobytes"]["longitude"])
		
		# result = urlfetch.fetch("http://api.hostip.info/?ip=" + template_values["ip"])
		# 		if result.status_code == 200:
		# 			dom = result.content
		# 			reg = re.compile('coordinates>([^<]+)', re.M)
		# 			m = reg.findall(result.content)
		# 			if len(m) > 0:
		# 				latlng = m[0].partition(',')
		# 				template_values["latlng"] = latlng[2] + "," + latlng[0]
		# 		
		# 	
		# 				result = urlfetch.fetch("http://maps.googleapis.com/maps/api/geocode/json?latlng=" + template_values["latlng"] + "&sensor=false")
		# 				if result.status_code == 200:
		# 					location = simplejson.loads(result.content)
		# 					if location["results"] and location["results"][0]:
		# 						for item in location["results"][0]["address_components"]:
		# 							if item["types"][0] == "postal_code":
		# 								template_values["zip"] = item["short_name"]
		# 								break

		#result = urlfetch.fetch("http://www.fcc.gov/cgi-bin/maps/coverage.pl?startpoint=" + template_values["latlng"])
		#if result.status_code == 200:
			
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))


class GetCoverage(webapp.RequestHandler):
	def get(self):
		latlng = self.request.get("latlng")
		result = urlfetch.fetch("http://www.fcc.gov/cgi-bin/maps/coverage.pl?startpoint=" + latlng + "&expert=1")
		if result.status_code == 200:
			reg = re.compile('FOX.+?>([^<]+)', re.M | re.S)
			m = reg.findall(result.content)
			channel = m[0]
			self.response.out.write(channel)

class GetChannels(webapp.RequestHandler):
	def get(self):
		channel = {
			"status": "invalid input"
		}
		latlon = self.request.get("latlon")
		
		if latlon:
			latlon = latlon.partition(",")
		
		try:
			if len(latlon) > 1:
				lat = round(float(latlon[0]), 1)
				lon = round(float(latlon[2]), 1)
				geo = db.GeoPt(lat, lon)
			
				q = Channel.all()
				q.filter("latlon =", geo)
				results = q.fetch(1)
			
				channel = {
					"latlon": [lat, lon],
					"status": "no results"
				}
			
				if len(results) > 0:
					channelModel = results[0]
					channel = {
						"network": channelModel.network,
						"virtual": channelModel.virtual,
						"callsign": channelModel.callsign,
						"latlon": [channelModel.latlon.lat, channelModel.latlon.lon],
						"status": "OK"
					}
				else:
					channel = getFCCChannel(geo, "FOX")
					
					channelModel = Channel(network=channel["network"],
											virtual=channel["virtual"],
											callsign="UNKNOWN",
											latlon=geo)
					channelModel.put()
					channel = {
						"network": channelModel.network,
						"virtual": channelModel.virtual,
						"callsign": channelModel.callsign,
						"latlon": [channelModel.latlon.lat, channelModel.latlon.lon],
						"status": "saved"
					}
		except:
			channel = {
				"status": "ex.message"
			}
			self.response.out.write(simplejson.dumps(channel))
		else:
			self.response.out.write(simplejson.dumps(channel))


class GetLocation(webapp.RequestHandler):
	def get(self):
		ip = self.request.get("ip")
		q = self.request.get("q")
		
		if len(ip) < 1:
			ip = self.request.remote_addr
		
		if ip == "127.0.0.1":
			ip = "24.22.211.139"
			
		location = {
			"ip": ip,
			"status": "no response"
		}
		
		result = urlfetch.fetch("http://api.hostip.info/?ip=" + ip)
		if result.status_code == 200:
			dom = result.content
			reg = re.compile('coordinates>([^<]+)', re.M)
			m = reg.findall(result.content)
			if len(m) > 0:
				latlng = m[0].partition(',')
				geo = db.GeoPt(latlng[2] + "," + latlng[0])
				location = {
					"ip": ip,
					"status": "OK",
					"latlon": str(geo)
				}
				
		if len(q) > 0:
			qlatlon = getGoogleLocation(q)
			channel = getFCCChannel(qlatlon, "FOX")
			if "virtual" not in channel:
				channel["virtual"] = "not found"
				
			self.redirect("/?q=" + q + "&iplatlon=" + location["latlon"] + "&qlatlon=" + str(qlatlon) + "&v=" + channel["virtual"])
		else:
			self.response.out.write(location)
		
				# result = urlfetch.fetch("http://maps.googleapis.com/maps/api/geocode/json?latlng=" + template_values["latlng"] + "&sensor=false")
				# if result.status_code == 200:
				# 	location = simplejson.loads(result.content)
				# 	if location["results"] and location["results"][0]:
				# 		for item in location["results"][0]["address_components"]:
				# 			if item["types"][0] == "postal_code":
				# 				template_values["zip"] = item["short_name"]
				# 				break
		# postal_code = self.request.get("zip")
		# result = urlfetch.fetch("http://www.fcc.gov/cgi-bin/maps/coverage.pl?startpoint=" + postal_code)
		# if result.status_code == 200:
		# 	self.response.out.write(result.content)

def getFCCChannel(geo, network):
	latlon = str(geo)
	channel = {
		"latlon": latlon,
		"network": network,
		"status": "no response"
	}
	result = urlfetch.fetch("http://www.fcc.gov/cgi-bin/maps/coverage.pl?startpoint=" + latlon + "&expert=1")
	if result.status_code == 200:
		reg = re.compile(network + '.+?>([^<]+)', re.M | re.S)
		m = reg.findall(result.content)
		if len(m) > 0:
			channel = {
				"latlon":latlon,
				"network":network,
				"virtual":m[0]
			}

	return channel
	
def getGoogleLocation(q):
	geo = None
	
	result = urlfetch.fetch("http://maps.googleapis.com/maps/api/geocode/json?address=" + q + "&sensor=false")
	if result.status_code == 200:
		json = simplejson.loads(result.content)
		lat = json["results"][0]["geometry"]["location"]["lat"]
		lon = json["results"][0]["geometry"]["location"]["lng"]
		geo = db.GeoPt(str(lat) + "," + str(lon))
		
	return geo	

def main():
    application = webapp.WSGIApplication([('/', MainHandler),
										('/channels', GetChannels),
										('/location', GetLocation)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
