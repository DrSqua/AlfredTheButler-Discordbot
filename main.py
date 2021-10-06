# bot.py

from alfred_commands import *
from alfred_repyclass import CheckContent
import youtube_dl

cur_path = os.path.dirname(__file__)
with open(cur_path + "/alfred-files/alfred-bot_token.txt") as bestand:
    TOKEN = bestand.readline()

client = discord.Client()

dbname = "alfred_response-database.db"
autorespond, alfred_autoresponse, alfred_cc = load_data(dbname)
song_queue = []

check_object = CheckContent(client)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    if message.author == client.user or message.author.bot:  # Check of het een mens is
        return
    check_object.update_source(discord_source=message)
    run, function = check_object.message_checker(response_dictionary=autorespond, alfred_dictionary=alfred_autoresponse,
                                                 cc_dictionary=alfred_cc)
    if isinstance(function, str):
        await eval(function + ")")
    await run


@client.event
async def join_voicechannel(discord_message):
    print("join_voicechannel command")
    if discord_message.author.voice is None:
        await discord_message.reply("Sir, you're not in a voice channel", mention_author=False)
    voice_channel = discord_message.author.voice.channel
    print(voice_channel)
    if voice_channel:
        await voice_channel.connect()
    else:
        await discord_message.voice_client.move_to(voice_channel)


@client.event
async def leave_voicechannel(discord_message):
    print('leave_voicechannel command')
    voice_client = client.voice_clients[0]
    await voice_client.disconnect()


@client.event
async def play_song(discord_message):
    global song_queue
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    YDL_OPTIONS = {'format': "bestaudio"}
    voice_client = client.voice_clients[0]
    url = discord_message.content.replace('play ', '').strip()
    if url == "":
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    print("URL === " + str(url))
    song_queue.append(url)
    print(song_queue)
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(song_queue[0], download=False)
        ydl_url = info['formats'][0]["url"]
        source = await discord.FFmpegOpusAudio.from_probe(ydl_url, method="fallback", **FFMPEG_OPTIONS)
        voice_client.play(source)
        print("Song ended?")


@client.event
async def pause_song(discord_message):
    print('pause_song command')
    voice_client = client.voice_clients[0]
    await voice_client.pause()


@client.event
async def resume_song(discord_message):
    print('resume_song command')
    voice_client = client.voice_clients[0]
    await voice_client.resume()


@client.event
async def return_queue(discord_message):
    global song_queue
    await discord_message.reply(str(song_queue), mention_author=False)


@client.event
async def clear_queue(discord_message):
    global song_queue
    song_queue = []
    await discord_message.reply("Cleared the channel, sir", mention_author=False)


client.run(TOKEN)
