from random import choice
import os
import discord
from AlfredReply_class import AlfredReply
from AlfredReply_class import AlfredCommand
from alfred_database import load_dictionary

def load_data(dbname):  # Database naar RAM
    autorespond = load_dictionary(dbname, "Generic")
    alfred_autoresponse = load_dictionary(dbname, "Alfred")
    alfred_cc = load_dictionary(dbname, "cc")
    print("Data loaded into RAM memory")
    return autorespond, alfred_autoresponse, alfred_cc


def check_autorespond_dict(response_dictionary, message,
                           return_multiple=False):  # Takes a dictionary and a long string, returns value in dict
    match = [key_tupl for key_tupl in tuple(response_dictionary.keys()) if
             [key for key in key_tupl if key in message]]  # List comprehensions for the w
    if match:  # If match is not Empty
        if return_multiple:  # If you want to return multiple
            return tuple([response_dictionary.get(key) for key in match])  # Give all values returned in a tuple
        else:
            key_len = tuple(map(lambda x: len(max(x, key=len)), match))  # Returns tuple of len(key_tuple)
            return response_dictionary.get(match[key_len.index(
                max(key_len))])  # Gets the index of max len, then uses index for key in match[] then returs value
    else:
        return False


def unpack_alfredreply(discord_message, alfredreply):  # Converts AlfredReply to a messageable discord.py
    endconvo = alfredreply.check_if_endconvo()
    # WITH FILE
    if alfredreply.check_file() != "None":
        cur_path = os.path.dirname(__file__)
        filepath = cur_path + alfredreply.check_file()
        if alfredreply.check_if_reply():
            return endconvo, discord_message.reply(content=alfredreply.check_message(), file=discord.File(filepath),
                                                   mention_author=alfredreply.check_if_mentionauthor())
        else:
            channel = discord_message.channel
            return endconvo, channel.send(content=alfredreply.check_message(), file=filepath,
                                          mention_author=alfredreply.check_if_mentionauthor())
    # ZONDER FILE
    else:
        if alfredreply.check_if_reply():
            return endconvo, discord_message.reply(content=alfredreply.check_message(),
                                                   mention_author=alfredreply.check_if_mentionauthor())
        else:
            channel = discord_message.channel
            return endconvo, channel.send(content=alfredreply.check_message(),
                                          mention_author=alfredreply.check_if_mentionauthor())

def handle_alfred(discord_message, alfred_autoresponse, alfred_cc):
    # Alfred cc
    custom_command = check_autorespond_dict(response_dictionary=alfred_cc, message=discord_message.content)
    # Geeft tuple terug, dus eerste element nodig

    if custom_command:
        return unpack_alfredcc(discord_message=discord_message, custom_command=custom_command[0])
    else:
        autorespond = check_autorespond_dict(response_dictionary=alfred_autoresponse,
                                             message=discord_message.content)  # Tuple of AlfredReply objects
        if autorespond:
            endconvo, reply = unpack_alfredreply(discord_message=discord_message,
                                                 alfredreply=choice(autorespond))
            return endconvo, reply
        else:
            return False, False

def unpack_alfredcc(discord_message, custom_command):
    dispatcher = {'play_song': "play_song(discord_message)",
                  'leave_voicechannel': "leave_voicechannel(discord_message)",
                  'join_voicechannel': "join_voicechannel(discord_message)"}
    function = dispatcher.get(custom_command.check_function())
    eval(function)
    endconvo, reply = unpack_alfredreply(discord_message=discord_message,
                                         alfredreply=custom_command.check_reply())
    return endconvo, reply

def main():
    generic_autorespond_dict = {("fy", "no", "fuckyou"): (
    AlfredReply("My sincerest apologies, sir"), AlfredReply("I must've made a mistake, my excuses")),
                                # Negative, apologetic
                                ("ty", "thankyou", "goodjob"): (
                                AlfredReply("My pleasure sir"), AlfredReply("It was of no effort, sir"),
                                AlfredReply("My pleasure, sir", "It was my pleasure, sir"))  # Thankfull
                                }
    cc1 = choice(check_autorespond_dict(generic_autorespond_dict, "fy"))
    print(cc1)


if __name__ == '__main__':
    main()
