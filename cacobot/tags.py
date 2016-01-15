import cacobot.base as base
import json, random, urllib.request, urllib.parse, discord

# json to load tags and config
# random to generate random emojis for orphan
# urllibs to post configs to pastebin

with open('configs/config.json') as data:
    config = json.load(data)

@base.cacofunc
def tag(message, client, *args, **kwargs):
    '''
    **.tag** <create | delete | edit | rename | gift | list | *tag id*> [mine | *content* | *tag id*] [*content* | *new id* | *new content* | *mention*]
    Allows you to manage tags.
    **.tag create [*id*] [*content*]** will create a new tag with the id [id] and content [content].
    **.tag delete [*id*]** will let you delete a tag, as long as you own it.
    **.tag edit [*id*] [*new content*]** will change [*id*]'s content to [*new content*].
    **.tag rename [*id*] [*new id*]** will change a tag's id to [*new id*].
    **.tag gift [*id*] [*mention*]** will change the owner of the tag to [*mention*].
    **.tag orphan [*id*]** will orphan a tag, allowing anyone to become the owner.
    **.tag claim [*id*]** lets you claim a tag that has been orphaned.
    **.tag list** will DM you all of the tags created in this server.
    **.tag list all** will list ALL of the tags CacoBot has.
    **.tag list mine** will DM you all of the tags you personally own.
    If you paste the resulting `list` message back in a channel CacoBot is listening to (including the "Retrieving tags owned by" part) CacoBot will tell you the number of tags it calculated.
    **.tag list orphaned** will DM you all of the tags that have no owner.
    **.tag [*id*]** will puke the tag with the id [*id*].
    **.tag [*id*] [*content*]** will implicitly create a tag if it can't find one.
    *Example: `.tag create gitgud http://i.imgur.com/Y3AZ1uX.jpg`*
    *(If a bot in your server already has tags, use their implementation, please. You can still use our tags, though. We have the AOE II taunts under tags 01-30! Try `.tag 08` and see what we mean!)*
    '''

    # Each tag has three objects: ['tag'], ['server'] and ['owner']. ['tag'] is the tag
    # itself, ['owner'] is the id of the tag's owner, and ['server] is the ID of the
    # server the tag was created on. ['owner'] and ['server'] can be "None" (as a
    # string) if nobody owns it.

    # I think Discord strips server-side already, but you can never be too careful.
    if message.content.strip() == '.tag':
        yield from client.send_message(message.channel, 'If you need help on using .tag, call .help tag!')
    else:
        # Load tags
        with open('configs/tags.json') as data:
            tags = json.load(data)

        cmd = message.content.split(' ')[1] #[0] is ".tag"

        # These commands all use the same params
        if cmd in ['create', 'delete', 'gift', 'list', 'edit', 'orphan', 'claim']:
            params = message.content.split(' ', 3)[1:]

            if cmd == 'create':
                if params[1] in tags:
                    yield from client.send_message(message.channel, ':no_entry_sign: The tag {} already exists. (It looks like this:)\n{}'.format(params[1], tags[params[1]]['tag']))
                else:
                    tags[params[1]] = {
                        'tag': params[2],
                        'owner': message.author.id
                    }
                    if not message.channel.is_private:
                        tags[params[1]]['server'] = message.server.id
                    else:
                        tags[params[1]]['server'] = 'None'
                    yield from client.send_message(message.channel, ':heavy_check_mark: Successfully created the tag `{}`.'.format(params[1]))

            elif cmd == 'delete':
                if params[1] in tags:
                    if message.author.id == tags[params[1]]['owner'] or (not message.channel.is_private and message.channel.permissions_for(message.author).manage_roles):
                        tags.pop(params[1])
                        yield from client.send_message(message.channel, ':heavy_check_mark: Successfully deleted the tag `{}`.'.format(params[1]))
                    else:
                        if tags[params[1]]['owner'] == 'None':
                            yield from client.send_message(message.channel, '{} This tag is **orphaned**. You can claim ownership with `.tag claim {}`'.format(random.choice([':boy:', ':girl:']), params[1]))
                        else:
                            yield from client.send_message(message.channel, ':no_entry_sign: You do not have permission to modify this tag.')
                else:
                    yield from client.send_message(message.channel, ':no_entry_sign: The tag `{}` could not be found.'.format(params[1]))

            elif cmd == 'gift':
                if params[1] in tags:
                    if tags[params[1]]['owner'] == message.author.id:
                        if message.mentions:
                            tags[params[1]]['owner'] = message.mentions[0].id
                            yield from client.send_message(message.channel, ':heart: {}: {} has gifted you the tag `{}`.'.format(message.mentions[0].mention, message.author.mention, params[1]))
                        else:
                            yield from client.send_message(message.channel, ':no_entry_sign: You did not specify a user to gift the tag to.')
                    else:
                        if tags[params[1]]['owner'] == 'None':
                            yield from client.send_message(message.channel, '{} This tag is **orphaned**. You can claim ownership with `.tag claim {}`'.format(random.choice([':boy:', ':girl:']), params[1]))
                        else:
                            yield from client.send_message(message.channel, ':no_entry_sign: You do not have permission to modify this tag.')
                else:
                    yield from client.send_message(message.channel, ':no_entry_sign: The tag `{}` could not be found.'.format(params[1]))

            elif cmd == 'list':
                if len(params) > 1:
                    if params[1] == 'mine':
                        lst = 'Retrieving tags owned by {}:\n\n'.format(message.author.name)

                        dect = {}
                        for x in [x for x in tags if tags[x]['owner'] == message.author.id]:
                            serv = discord.utils.find(lambda y: y.id == tags[x]['server'], client.servers)
                            if serv == None:
                                if 'Direct Messages' in dect:
                                    dect['Direct Messages'].append(x)
                                else:
                                    dect['Direct Messages'] = [x]
                            else:
                                if serv.name in dect:
                                    dect[serv.name].append(x)
                                else:
                                    dect[serv.name] = [x]

                        for x in dect:
                            lst += '{}\n=======================\n'.format(x)
                            for y in dect[x]:
                                lst += y + ' '
                            lst += '\n\n'

                        values = {
                          'api_dev_key' : config['pastebin_key'],
                          'api_option' : 'paste',
                          'api_paste_code' : lst,
                          'api_paste_private' : '1',
                          'api_paste_expire_date' : '10M'
                        }

                        data = urllib.parse.urlencode(values)
                        data = data.encode('utf-8') # data should be bytes
                        req = urllib.request.Request('http://pastebin.com/api/api_post.php', data)

                        with urllib.request.urlopen(req) as response:
                            api_response = response.read().decode("utf-8")

                        yield from client.send_message(message.author, api_response)
                    elif params[1] == 'orphaned':
                        lst = 'These tags have no owner and can be claimed:\n\n'

                        for x in [x for x in tags if tags[x]['owner'] == 'None']:
                            lst += x + ' '

                        values = {
                          'api_dev_key' : config['pastebin_key'],
                          'api_option' : 'paste',
                          'api_paste_code' : lst,
                          'api_paste_private' : '1',
                          'api_paste_expire_date' : '10M'
                        }

                        data = urllib.parse.urlencode(values)
                        data = data.encode('utf-8') # data should be bytes
                        req = urllib.request.Request('http://pastebin.com/api/api_post.php', data)

                        with urllib.request.urlopen(req) as response:
                            api_response = response.read().decode("utf-8")

                        yield from client.send_message(message.author, api_response)
                    elif params[1] == 'all':
                        lst = 'Here\'s a list of all the tags I know.\n\n'

                        dect = {}
                        for x in tags:
                            if tags[x]['owner'] == 'None':
                                if 'Orphaned' in dect:
                                    dect['Orphaned'].append(x)
                                else:
                                    dect['Orphaned'] = [x]
                            else:
                                if tags[x]['server'] == 'None':
                                    if 'Direct Messages' in dect:
                                        dect['Direct Messages'].append(x)
                                    else:
                                        dect['Direct Messages'] = [x]
                                else:
                                    if discord.utils.find(lambda y: y.id == tags[x]['server'], client.servers).name in dect:
                                        dect[discord.utils.find(lambda y: y.id == tags[x]['server'], client.servers).name].append(x)
                                    else:
                                        dect[discord.utils.find(lambda y: y.id == tags[x]['server'], client.servers).name] = [x]

                        for x in dect:
                            lst += '{}\n=======================\n'.format(x)
                            for y in dect[x]:
                                lst += y + ' '
                            lst += '\n\n'

                        values = {
                          'api_dev_key' : config['pastebin_key'],
                          'api_option' : 'paste',
                          'api_paste_code' : lst,
                          'api_paste_private' : '1',
                          'api_paste_expire_date' : '10M'
                        }

                        data = urllib.parse.urlencode(values)
                        data = data.encode('utf-8') # data should be bytes
                        req = urllib.request.Request('http://pastebin.com/api/api_post.php', data)

                        with urllib.request.urlopen(req) as response:
                            api_response = response.read().decode("utf-8")

                        yield from client.send_message(message.author, api_response)
                else:
                    if message.channel.is_private:
                        lst = 'Here\'s a list of all the tags created in direct messages with me.\n\n'
                    else:
                        lst = 'Here\'s a list of all the tags created in the {} server.\n\n'.format(message.server.name)
                    if not message.channel.is_private:
                        for x in [x for x in tags if tags[x]['server'] == message.server.id]:
                            lst += x + ', '
                    else:
                        for x in [x for x in tags if tags[x]['server'] == 'None']:
                            lst += x + ', '
                    lst = lst[:-2]

                    values = {
                      'api_dev_key' : config['pastebin_key'],
                      'api_option' : 'paste',
                      'api_paste_code' : lst,
                      'api_paste_private' : '1',
                      'api_paste_expire_date' : '10M'
                    }

                    data = urllib.parse.urlencode(values)
                    data = data.encode('utf-8') # data should be bytes
                    req = urllib.request.Request('http://pastebin.com/api/api_post.php', data)

                    with urllib.request.urlopen(req) as response:
                        api_response = response.read().decode("utf-8")

                    yield from client.send_message(message.author, api_response)

            elif cmd == 'edit':
                if params[1] in tags:
                    if tags[params[1]]['owner'] == message.author.id:
                        tags[params[1]]['tag'] = params[2]
                        yield from client.send_message(message.channel, ':heavy_check_mark: Successfully edited the tag `{}`.'.format(params[1]))
                    else:
                        if tags[params[1]]['owner'] == 'None':
                            yield from client.send_message(message.channel, '{} This tag is **orphaned**. You can claim ownership with `.tag claim {}`'.format(random.choice([':boy:', ':girl:']), params[1]))
                        else:
                            yield from client.send_message(message.channel, ':no_entry_sign: You do not have permission to modify this tag.')
                else:
                    yield from client.send_message(message.channel, ':no_entry_sign: The tag `{}` could not be found.'.format(params[1]))

            elif cmd == 'orphan':
                if params[1] in tags:
                    if tags[params[1]]['owner'] == message.author.id:
                        tags[params[1]]['owner'] = 'None'
                        tags[params[1]]['server'] = 'None'
                        yield from client.send_message(message.channel, '{} You have orphaned the tag `{}`.'.format(random.choice([':boy:', ':girl:']), params[1]))
                    else:
                        if tags[params[1]]['owner'] == 'None':
                            yield from client.send_message(message.channel, '{} This tag is **orphaned**. You can claim ownership with `.tag claim {}`'.format(random.choice([':boy:', ':girl:']), params[1]))
                        else:
                            yield from client.send_message(message.channel, ':no_entry_sign: You do not have permission to modify this tag.')
                else:
                    yield from client.send_message(message.channel, ':no_entry_sign: The tag `{}` could not be found.'.format(params[1]))

            elif cmd == 'claim':
                if params[1] in tags:
                    if tags[params[1]]['owner'] == 'None':
                        tags[params[1]]['owner'] = message.author.id
                        if not message.channel.is_private:
                            tags[params[1]]['server'] = message.server.id
                        else:
                            tags[params[1]]['server'] = 'None'
                        yield from client.send_message(message.channel, ':children_crossing: You have claimed the tag `{}`.'.format(params[1]))
                    else:
                        yield from client.send_message(message.channel, ':no_entry_sign: This tag is owned by <@{}>.'.format(tags[params[1]]['owner']))
                else:
                    yield from client.send_message(message.channel, ':no_entry_sign: The tag `{}` could not be found.'.format(params[1]))

        elif cmd == 'rename':
            params = message.content.split(' ')[1:]
            if params[1] in tags:
                if tags[params[1]]['owner'] == message.author.id:
                    tags[params[2]] = tags.pop(params[1])
                    yield from client.send_message(message.channel, ':heavy_check_mark: Successfully renamed the tag `{}` to `{}`.'.format(params[1], params[2]))
                else:
                    if tags[params[1]]['owner'] == 'None':
                        yield from client.send_message(message.channel, '{} This tag is **orphaned**. You can claim ownership with `.tag claim {}`'.format(random.choice([':boy:', ':girl:']), params[1]))
                    else:
                        yield from client.send_message(message.channel, ':no_entry_sign: You do not have permission to modify this tag.')
            else:
                yield from client.send_message(message.channel, ':no_entry_sign: The tag `{}` could not be found.'.format(params[1]))

        else:
            params = message.content.split(' ', 2)[1:]
            if cmd in tags:
                yield from client.send_message(message.channel, tags[cmd]['tag'])
            else:
                if len(params) > 1:
                    tags[params[0]] = {
                        'tag': params[1],
                        'owner': message.author.id
                    }
                    if not message.channel.is_private:
                        tags[params[0]]['server'] = message.server.id
                    else:
                        tags[params[0]]['server'] = 'None'
                    yield from client.send_message(message.channel, ':heavy_check_mark: Successfully created the tag `{}`.'.format(params[0]))

                else:
                    yield from client.send_message(message.channel, ':no_entry_sign: The tag {} could not be found.'.format(cmd))

        #re-save tags.json
        with open('configs/tags.json', 'w') as file:
            json.dump(tags, file, indent=4)
