#!/usr/bin/env python
# encoding: utf-8

import datetime
import dateutil.parser
import hypchat
import logging
import os
import pytz
import sys
import time
import threading

logging.basicConfig(level=logging.INFO)

class Hipbot(object):

	"""A bot for hipchat"""

	def __init__(self, api_url, token, username, *rooms):
		"""Create the bot. api_url and token are required

		:api_url: TODO
		:token: TODO
		:rooms: All of the roomnames the hipbot needs to watch

		"""
		self._api_url = api_url
		self._token = token
		self._room_names = rooms
		self._poll_amt = 10
		self._username = username

		self._rooms_map = {}
		self._rooms_last_msg = {}

		self._running = threading.Event()
		self._log = logging.getLogger("hipbot")

		self._hipchat = hypchat.HypChat(token, endpoint=api_url)

		self._reactives = []
		self._non_reactives = []
	
	def add_reactive(self, reactive):
		"""Add a reactive plugin (function) to this hipbot. E.g.

		```
		def shutup(room, message, bot, hipchat):
			if random.random() > 0.9:
				message.from.message("shutup!")

		bot.add_reactive(shutup)
		```
		"""
		self._reactives.append(reactive)
	
	def add_non_reactive(self, non_reactive):
		"""Add a non-reactive plugin (function) to this hipbot. E.g.

		```
		def read_this(bot, hipchat):
			# get interesting things to read
			link_infos = get_link_infos(...)

			if len(link_infos) > 0:
				update = "\n\n".join(["{} : {}".format(blurb, link) for blurb,link in link_infos)
				for room in bot.rooms:
					room.message(update)

		bot.add_non_reactive(read_this)
		```
		"""
		self._non_reactives.append(non_reactive)

	def run(self):
		"""Run the hipbot
		"""
		self._running.set()

		self.rooms = self._fetch_room_infos(*self._room_names)

		self._fetch_users()
		if self._username in self._user_map:
			self.user = self._user_map[self._username]
		else:
			raise Exception("username not found? TODO hash this out some more")

		now = lambda: datetime.datetime.now(pytz.utc)

		# pretend we have a bit of catching up to do
		while self._running.is_set():
			for room in self.rooms:
				new_messages = self._fetch_new_room_messages(room)
				if len(new_messages) > 0:
					self._process_messages(room, new_messages)

			self._run_non_reactives()

			time.sleep(self._poll_amt)

	# ------------------------
	# private methods
	# ------------------------

	def _fetch_users(self):
		self._user_map = {}
		res = self._hipchat.users()
		for user in res["items"]:
			self._user_map[user.name] = user
			self._user_map[user.id] = user
	
	def _fetch_room_infos(self, *room_names):
		self._rooms_map = {}
		self._rooms_last_msg = {}

		res = self._hipchat.rooms()
		rooms = []
		for room in res["items"]:
			self._rooms_map[room.id] = room
			self._rooms_map[room.name] = room
			if room["name"] in room_names:
				rooms.append(room)

		return rooms
	
	def _fetch_new_room_messages(self, room):
		last_msg = self._rooms_last_msg.setdefault(room.id, None)

		if last_msg is None:
			messages = room.history()["items"]
			# so we don't reply to every single message that has occurred today
			if len(messages) > 0:
				last_msg = messages[-1]
				self._rooms_last_msg[room.id] = last_msg
				return []
		else:
			messages = room.latest(not_before=last_msg["id"])["items"]

		real_messages = []
		for message in messages:
			from_ = message["from"]
			if message["id"] == last_msg["id"]:
				continue
			if hasattr(from_, "id") and from_.id != self.user.id:
				real_messages.append(message)
			elif from_ != self.user.id and from_ != self.user.name:
				real_messages.append(message)
			last_msg = message

		self._rooms_last_msg[room.id] = last_msg

		return real_messages
	
	def _process_messages(self, room, new_messages):
		"""Process the new messages
		"""
		for message in new_messages:
			self._log.info("handling message {}".format(message["id"]))

			for reactive in self._reactives:
				try:
					reactive(room, message, self, self._hipchat)
				except Exception as e:
					self._log.error("reactive {!r} errored while handling message".format(reactive), exc_info=True)

	def _run_non_reactives(self):
		for non_reactive in self._non_reactives:
			try:
				non_reactive(self, self._hipchat)
			except Exception as e:
				self._log.error("non-reactive {!r} errored while running".format(non_reactive), exc_info=True)
