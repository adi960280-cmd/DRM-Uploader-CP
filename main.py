import os
import re
import time
import requests
import m3u8
from aiohttp import ClientSession
from pyrogram import Client
from pyrogram.errors import FloodWait

# Your bot initialization
bot = Client("my_bot")  # replace with your actual Client initialization

async def process_links(links, count, helper, MR, b_name, raw_text2, res, photo, thumb):
    for i, V in enumerate(links):
        try:
            url = "https://" + V

            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(
                        url,
                        headers={
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                            'Accept-Language': 'en-US,en;q=0.9',
                            'Cache-Control': 'no-cache',
                            'Connection': 'keep-alive',
                            'Pragma': 'no-cache',
                            'Referer': 'http://www.visionias.in/',
                            'Sec-Fetch-Dest': 'iframe',
                            'Sec-Fetch-Mode': 'navigate',
                            'Sec-Fetch-Site': 'cross-site',
                            'Upgrade-Insecure-Requests': '1',
                            'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
                            'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
                            'sec-ch-ua-mobile': '?1',
                            'sec-ch-ua-platform': '"Android"',
                        },
                    ) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

            elif 'videos.classplusapp' in url or 'media-cdn.classplusapp.com' in url:
                tokencp = 'YOUR_TOKEN_HERE'
                url = requests.get(
                    f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}',
                    headers={'x-access-token': tokencp}
                ).json()['url']

            elif "apps-s3-jw-prod.utkarshapp.com" in url:
                if 'enc_plain_mp4' in url:
                    url = url.replace(url.split("/")[-1], res+'.mp4')
                elif 'Key-Pair-Id' in url:
                    url = None
                elif '.m3u8' in url:
                    q = m3u8.loads(requests.get(url).text).data['playlists'][1]['uri'].split("/")[0]
                    x = url.split("/")[5]
                    x = url.replace(x, "")
                    url = m3u8.loads(requests.get(url).text).data['playlists'][1]['uri'].replace(q+"/", x)

            elif "edge.api.brightcove.com" in url:
                bcov = 'YOUR_BRIGHTCOVE_AUTH'
                url = url.split("bcov_auth")[0] + bcov

            elif ".pdf" in url:
                url = url.replace(" ", "%20")

            # Clean video name
            name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            name = f'{str(count).zfill(3)})😎𝖘cᾰ𝗺𝗺ⲉ𝗿:)™~{name1[:60]}'
            ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"

            # Prepare yt-dlp command
            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

            # Prepare captions
            cc = f'**[ 🎥 ] 𝗩𝗜𝗗 𝗜𝗗 : {str(count).zfill(3)}\n**\n**𝐕𝐢𝐝𝐞𝐨 𝐓𝐢𝐭𝐥𝐞** : {name1}**({res}):)**.mp4\n\n**<pre>⭐️𝗕𝗔𝗧𝗖𝗛 𝗡𝗔𝗠𝗘** » **{b_name} </pre>**\n\n**𝐄𝐱𝐭𝐫𝐚𝐜𝐭𝐞𝐝 𝐁𝐲 ➤ {MR}**\n\n'

            # Download and send
            try:
                if "drive" in url:
                    ka = await helper.download(url, name)
                    copy = await bot.send_document(chat_id=m.chat.id, document=ka, caption=cc)
                    count += 1
                    os.remove(ka)
                    time.sleep(5)

                elif ".pdf" in url:
                    download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                    os.system(download_cmd)
                    copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc)
                    count += 1
                    os.remove(f'{name}.pdf')

                elif "youtu" in url:
                    await bot.send_photo(chat_id=m.chat.id, photo=photo, caption=cc)
                    count += 1

                else:
                    Show = f"**⚡Downloading Started...**\n**Name:** {name}\nQuality: {raw_text2}\nURL: {url}"
                    prog = await m.reply_text(Show)
                    res_file = await helper.download_video(url, cmd, name)
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                    count += 1
                    time.sleep(10)

            except FloodWait as e:
                await m.reply_text(str(e))
                time.sleep(e.x)
                continue

        except Exception as e:
            await m.reply_text(f"Downloading failed\n{str(e)}\nName: {name}\nLink: {url}")

# Run the bot
bot.run()
