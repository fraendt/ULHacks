import aiohttp
import asyncio
from bs4 import BeautifulSoup

# get title, image, description, url of wikihow article
async def wikihow_random():
    url = 'https://www.wikihow.com/Special:Randomizer'
    ret = {}
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resolved_url = resp.url
            ret["url"] = resolved_url
            print(resolved_url)
            text = await resp.text()
            soup = BeautifulSoup(text, "html.parser")
            
            desc = soup.find("meta", {"property": "og:description"})
            if desc is None:
                desc = soup.find("meta", {"name": "description"})
            desc = desc["content"]
            ret["description"] = desc

            # returns url for image if possible, else None
            img = soup.find("meta", {"property": "og:image"})
            if img is not None:
                img = img["content"]
            ret["image"] = img

            # returns str for title if possible, else None
            title = soup.find("meta", {"property": "og:title"})
            if title is not None:
                title = title["content"]
            ret["image"] = title

            print(desc)

            return ret

asyncio.run(wikihow_random())
