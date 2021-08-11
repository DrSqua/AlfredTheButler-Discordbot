import discord
from random import choice
#DEES OPNIEUW DOEN
def check_for_txt2pic(message): #message as 'string'
    with open("string2photo.txt", 'r') as bestand:
        line = bestand.readline()
        while line != "":
            gesplitst = line.split(",")
            for naam in gesplitst[0].split("."):
                if naam in message.lower():
                    return True, gesplitst[1].strip()
            line = bestand.readline()
        return False, None

def check_for_autorespond_2text(message):
    string_dict = {("fyalfred", "noalfred"):("My sincerest apologies, sir", "I must've made a mistake, my excuses"), #Negative, apologetic
                   ("tyalfred",):("My pleasure sir", "It was of no effort, sir") #Thankfull
                   }
    bericht = message.content.lower().replace(' ', '').strip()
    #String_Dict items checken
    if any(x in bericht for x in [element for tupl in string_dict.keys() for element in tupl]): #Check of ge dees moet overlopen
        for input_tuple in string_dict.keys():
            for input in input_tuple:
                if input in bericht:
                    return next(value for keys, value in string_dict.items() if input in keys) #Beetje magie ma cv
    else:
        return None


def check_for_autorespond_2pic(message):
    pic_dict = {("purge", "burn", "destroy", "eliminate"):("purging.gif",),
                ("-play","!play"):("playthatfunkymusic.gif",)
                }
    bericht = message.content.lower().replace(' ', '').strip()
    #Pic_Dict items checker
    if any(x in bericht for x in [element for tupl in pic_dict.keys() for element in tupl]):  # Check of ge dees moet overlopen
        for input_tuple in pic_dict.keys():
            for input in input_tuple:
                if input in bericht:
                    return next(value for keys, value in pic_dict.items() if input in keys)  # Beetje magie ma cv

def check_content(message):
    #Basis hello check
    if message.content == "<@!473775789398163457>":
        return message.reply("At your service!", mention_author=False)
    #Zin autorespond checks

    #1 string autorespond checks naar txt
    check = check_for_autorespond_2text(message)
    if check is not None:
        return message.reply(choice(check), mention_author=False)

    #1 string autorespond checks naar pic
    check = check_for_autorespond_2pic(message)
    if check is not None:
        return message.reply(file=discord.File(choice(check)), mention_author=False)

def main():
    print(check_for_txt2pic("bap"))

if __name__ == '__main__':
    main()