# hipbot

A simple HipChat bot that exposes two "plugin" methods:

* reactive - processes any new messages in the subscribed rooms
* non-reactive - gets called every 10 seconds

## Reactive "Plugins"

A reactive "plugin" is simply a callable that has the signature below and processes new
messages in the subscribed rooms (reacts to them):

```python
def reactive(room, message, bot, hipchat):
	"""Reactive plugin

	:room: A Hypchat room object that the message was received in
	:message: The new message
	:bot: A reference to the Hipbot instance
	:hipchat: A reference to the raw hypchat client
	"""

	# do something useful
	room.message("a message to the room")

	# or maybe set the title
	room.title("the new title")

	# etc.

bot.add_reactive(reactive)
```

Reactive "plugins" are for each new message in a the subscribed rooms. Hipbot polls
HipChat for new messages every 10 seconds (hipchat has
a default rate limit of 100 API calls every 5 minutes, every 10 seconds gives some wiggle room).

Note that the room is a `hypchat` room object, and exposes the methods
defined in the ![room class](https://github.com/RafTim/HypChat/blob/master/hypchat/restobject.py#L118).

## Non-Reactive "Plugins"

A non-reactive "plugin" is simple a callable that has the signature below and is called every poll
period (does not react to new messages, is called EVERY poll period):

```python
last_time = None
def non_reactive(bot, hipchat):
	"""Non-Reactive plugin

	:bot: A reference to the Hipbot instance
	:hipchat: A reference to the raw hypchat client
	"""
	global last_time
	if last_time is None:
		last_time = time.time()
		return

	if time.time() - last_time > 60*60:
		for room in bot.rooms:
			room.message("The time is %d".format(time.time()))

bot.add_non_reactive(non_reactive)
```

# Sample Script

```python
import hipbot

def loler(room, message, bot, hipchat):
	if "lol" in message["message"].lower():
		room.message(u"@{} {}".format(
			message["from"].mention_name,
			"SO FUNNY! LOL! O.M.G!"
		))

if __name__ == "__main__":
	api_url = "https://url_to_hipchat"
	api_v2_token = "YOUR TOKEN"
	# full username, not the @mention name
	api_username = "USERNAME ASSOCIATED WITH THE TOKEN"

	# the rooms to "join"
	rooms = sys.argv[1:]

	bot = hipbot.Hipbot(
		api_url,
		api_v2_token,
		api_username,
		*rooms
	)
	bot.add_reactive(loler)
	bot.run()
```
