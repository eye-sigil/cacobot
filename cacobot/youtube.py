import json
import cacobot.base as base
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

youtube = build(base.config['youtube']['API_SERVICE_NAME'], base.config['youtube']['API_VERSION'], developerKey=base.config['youtube']['DEVELOPER_KEY'])

@base.cacofunc
async def yt(message, client, *args, **kwargs):
    '''
    **{0}yt** <*query*> [.results *int*]
    Searches YouTube and returns the first query. If you provide `.results` with an integer afterwards, returns the first *int* results.
    *Example: `{0}yt Doom E1M1 100% .results 3`*
    '''

    if message.content.split()[-2] == '.results':
        query = message.content[4:message.content.find('.results') - 2]
        results = int(message.content.split()[-1]) #The number of results to spew.
    else:
        query = message.content[4:]
        results = 1

    #This string will store the message that will eventually be sent.
    all_videos = ''

    #Limit requests if exceeds base.config
    if results > base.config['youtube']['request_limit']:
        all_videos += '*I had to limit your request to {} results at the behest of my maintainer.*\n'.format(base.config['youtube']['request_limit'])
        results = base.config['youtube']['request_limit']

    #this is all pretty much from the YouTube API Python example.

    search_response = youtube.search().list(
      q = query,
      part = 'id,snippet',
      maxResults = results,
      type = 'video'
    ).execute()

    vids = []

    for search_result in search_response.get('items', []):
        vids.append('**' + search_result['snippet']['title'] + '** | http://youtu.be/' + search_result['id']['videoId'])

    for video in range(0, len(vids)):
        all_videos += vids[video] + ' (Result ' + str(video + 1) + ' of ' + str(len(vids)) + ' from YouTube) \n\n'

    await client.send_message(message.channel, all_videos)

#@base.cacofunc
async def ytadd(message, client, *args, **kwargs):
    '''
    **{0}ytadd** [*query*]
    *This command was created for the /g/ discord server.*
    Searches YouTube for *query*, returns the first result, then clarifies with you before adding it to the queue for Memebot Jones. If you deny the result, returns the next result and tries again. This goes until 5 results have been displayed, or the bot recieves `abort`.
    *Example: `{0}ytadd meme machine`*
    '''

    query = message.content.split(None, 1)[1]

    search_response = youtube.search().list(
      q = query,
      part = 'id,snippet',
      maxResults = 5,
      type = 'video'
    ).execute()

    for search_result in search_response.get('items', []):
        await client.send_message(message.channel, 'I searched YouTube and got **{}**. Shall I add this video to the queue? (Reply **Y**es, **N**o, or **A**bort).\nhttp://youtu.be/{}'.format(search_result['snippet']['title'], search_result['id']['videoId']))

        success = False
        quit = False

        while not success:
            response = await client.wait_for_message(author=message.author, channel=message.channel)
            if response.content.lower() == 'yes' or response.content.lower() == 'y':
                await client.send_message(message.channel, '$add http://www.youtube.com/watch?v={}'.format(search_result['id']['videoId']))
                success = True
                quit = True
            elif response.content.lower() == 'no' or response.content.lower() == 'n':
                success = True
            elif response.content.lower() == 'abort' or response.content.lower() == 'a':
                await client.send_message(message.channel, 'Okay.')
                success = True
                quit = True
            else:
                await client.send_message(message.channel, 'Please say **Y**es, **N**o, or **A**bort.')

        if quit:
            break
ytadd.server = '/g/'
