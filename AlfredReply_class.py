from random import choice
class AlfredReply:
    def __init__(self, message=None, file=None, reply=True, mentionauthor=False, endconvo=True):
        self.__message = message
        self.__file = file
        self.__reply = reply
        self.__mentionauthor = mentionauthor
        self.__endconvo = endconvo

    def __str__(self):
        return str(self.__message) + "\n" + str(self.__file) + "\n" + str(self.__reply) + "\n" + str(self.__mentionauthor) + "\n" + str(self.__endconvo)

    def __repr__(self):
        return str(self.__message) + "\n" + str(self.__file) + "\n" + str(self.__reply) + "\n" + str(self.__mentionauthor) + "\n" + str(self.__endconvo)

    def check_message(self):
        return self.__message

    def check_file(self):
        return self.__file

    def check_if_reply(self):
        return self.__reply

    def check_if_mentionauthor(self):
        return self.__mentionauthor

    def check_if_endconvo(self):
        return self.__endconvo


class AlfredCommand:
    def __init__(self, function, reply):
        self.__reply = reply
        self.__function = function

    def __str__(self):
        return str(self.__function) +"\n"+ str(self.__reply)

    def __repr__(self):
        return str(self.__function) +"\n"+ str(self.__reply)

    def check_reply(self):
        return choice(self.__reply)

    def check_function(self):
        return self.__function