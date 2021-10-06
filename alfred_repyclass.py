import os
from random import choice

import discord


class AlfredReply:
    def __init__(self, message=None, file=None, reply=True, mentionauthor=False, endconvo=True):
        self.__message = message
        self.__file = file
        self.__reply = reply
        self.__mentionauthor = mentionauthor
        self.__endconvo = endconvo

    def __str__(self):
        return "AlfredReply object:" + "\n" + str(self.__message) + "\n" + str(self.__file) + "\n" + str(
            self.__reply) + "\n" + str(self.__mentionauthor) + "\n" + str(self.__endconvo)

    def __repr__(self):
        return "AlfredReply object:" + "\n" + str(self.__message) + "\n" + str(self.__file) + "\n" + str(
            self.__reply) + "\n" + str(self.__mentionauthor) + "\n" + str(self.__endconvo) + "\n"

    def check_endconvo(self):
        return self.__endconvo

    def send_message(self, discord_message):
        """WITH FILE ELSE WITHOUT"""
        if self.__file != "None":
            cur_path = os.path.dirname(__file__)
            filepath = cur_path + self.__file
            if self.__reply:
                return self.__endconvo, discord_message.reply(content=self.__message, file=discord.File(filepath),
                                                              mention_author=self.__mentionauthor)
            else:
                channel = discord_message.channel
                return self.__endconvo, channel.send(content=self.__message, file=discord.File(filepath),
                                                     mention_author=self.__mentionauthor)
        else:
            if self.__reply:
                return self.__endconvo, discord_message.reply(content=self.__message,
                                                              mention_author=self.__mentionauthor)
            else:
                channel = discord_message.channel
                return self.__endconvo, channel.send(content=self.__message,
                                                     mention_author=self.__mentionauthor)


class AlfredCC:
    def __init__(self, function=None, messages=None):
        if messages is None:
            messages = set(())
        self.__function = function
        self.__messages = messages

    def __str__(self):
        return "AlfredCC object" + self.__function + self.__messages

    def __repr__(self):
        return "AlfredCC object" + self.__function + self.__messages

    def run_function(self):
        return str(self.__function)

    def get_message(self):
        return choice(self.__messages)


class CheckContent:
    def __init__(self, client, discord_source=None):
        self.__client = client
        self.__discord_source = discord_source
        if self.__discord_source is not None:
            self.__discord_message = discord_source.content.lower().replace(' ', '').strip()
        self.__users_ready = set(())
        self.__replies = None
        self.__function = None

    def __str__(self):
        return str(self.__discord_source) + "\n" + str(self.__discord_message)

    def __repr__(self):
        return str(self.__discord_source) + "\n" + str(self.__discord_message)

    def update_source(self, discord_source):
        self.__discord_source = discord_source
        self.__discord_message = discord_source.content.lower().replace(' ', '').strip()

    def check_with_dict(self, response_dictionary, return_multiple):
        match = [key_tupl for key_tupl in tuple(response_dictionary.keys()) if
                 [key for key in key_tupl if key in self.__discord_message]]  # List comprehensions for the winnnn
        if match:  # If match is not Empty
            if return_multiple:  # If you want to return multiple
                return tuple([response_dictionary.get(key) for key in match])  # Give all values returned in a tuple
            else:
                key_len = tuple(map(lambda x: len(max(x, key=len)), match))  # Returns tuple of len(key_tuple)
                return response_dictionary.get(match[key_len.index(
                    max(key_len))])  # Gets the index of max len, then uses index for key in match[] then returs value
        else:
            return False

    def check_alfred_content(self, alfred_dictionary, cc_dictionary):
        """
        response = lookup keyword
        if no kw in cc_dict
            response = lookup kw in alfred_dict
            if no kw in alfred_dict
                return "sorry sir?" reply
            else
                kies message uit tuple lijst
                functie = None
        else (dus als command is gevonden)
            return (endconvo, message await, function)
        """
        response = self.check_with_dict(cc_dictionary, False)  # Returns Alfredcc
        if response is False:  # If not Alfredcc
            response = self.check_with_dict(alfred_dictionary, False)  # Returns tuple(AlfredReply)
            if response is False:
                return False, self.__discord_source.reply(content="sorry, sir?",
                                                              mention_author=False), None
            else:
                reply = choice(response)  # Chose 1 reply
                function = None
        else:
            function = response[0].run_function()  # Actions on Alfredcc
            reply = response[0].get_message()
        endconvo, message = reply.send_message(discord_message=self.__discord_source)
        return endconvo, message, function

    def message_checker(self, response_dictionary, alfred_dictionary, cc_dictionary):
        """
        if user in users_ready{}
            check content en get (endconvo, message await, function) as run
        elif Alfred in mentions
            add user to users_ready{}
            check content en get (endconvo, message, await, function) as run
        else
            response = check dict, get False or AlfredReply
            if not False
                return AlfredReply.send_message
        if run not empty
            if endconvo is True
                remove user from users_ready{}
            return message, function
        """
        if self.__discord_source.author in self.__users_ready:
            run = self.check_alfred_content(alfred_dictionary=alfred_dictionary, cc_dictionary=cc_dictionary)
        elif self.__client.user in self.__discord_source.mentions:
            self.__users_ready.add(self.__discord_source.author)
            run = self.check_alfred_content(alfred_dictionary=alfred_dictionary, cc_dictionary=cc_dictionary)
        else:
            response = self.check_with_dict(response_dictionary=response_dictionary, return_multiple=False)
            if response is False:
                return False, False
            else:
                endconvo, message = response[0].send_message(discord_message=self.__discord_source)
                run = endconvo, message, None
        if run is not None:
            if run[0] is True:
                self.__users_ready.remove(self.__discord_source.author)
            return run[1], run[2]