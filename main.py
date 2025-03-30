# Rifter 1.0
# Coded By Lain<3

import sys
import os
import asyncio

try:
  from rich.console import Console
  from rich.panel import Panel
  from dotenv import load_dotenv
  import discord
  import aiohttp
  import rift
except ImportError:
  print("Missing dependencies!")
  sys.exit(1)

load_dotenv()
console = Console()
intents = discord.Intents.all()
client = discord.Client(intents=intents)
TOKEN = os.getenv("TOKEN")
PREFIX = os.getenv("PREFIX")

def log(message):
  console.print(Panel.fit(message, title="RIFT BOT", style="bold cyan"))

@client.event
async def on_ready():
  log(f"Logged in as {client.user}")

@client.event
async def on_message(message):
  if message.author.bot:
    return

  cmd = "!rift"
  if message.content.startswith(cmd) and message.attachments:
    parts = message.content.split()
    mode = parts[1].lower() if len(parts) > 1 and parts[1] in ("recode", "decode") else "recode"

    input_folder = "re_in" if mode == "recode" else "de_in"
    output_folder = "re_out" if mode == "recode" else "de_out"

    attachment = message.attachments[0]
    input_file_path = f"{input_folder}/{attachment.filename}"
    output_file_path = f"{output_folder}/{attachment.filename}"

    os.makedirs(input_folder, exist_ok=True)
    await message.add_reaction("⏳")

    try:
      async with aiohttp.ClientSession() as session:
        async with session.get(attachment.url) as r:
          if r.status == 200:
            with open(input_file_path, "wb") as f:
              f.write(await r.read())

      log(f"Downloaded `{attachment.filename}`. Starting `{mode}` mode...")
      
      embed = discord.Embed(
        title="Processing File...",
        description=f"`{attachment.filename}` is being processed in `{mode}` mode.",
        color=discord.Color.blue()
      )
      embed.set_footer(text="Powered by FileRift by DanielSpaniel")
      status_msg = await message.channel.send(embed=embed)

      # Run rift.start
      await asyncio.to_thread(rift.start, mode)
      await asyncio.sleep(2)

      if os.path.exists(output_file_path):
        embed = discord.Embed(
          title="Processing Complete",
          description=f"`{attachment.filename}` has been processed successfully!",
          color=discord.Color.green()
        )
        embed.set_footer(text="Powered by FileRift by DanielSpaniel")
        await status_msg.edit(embed=embed)
        await message.channel.send(file=discord.File(output_file_path))
        os.remove(output_file_path)
        await message.add_reaction("✅")
      else:
        await message.add_reaction("❌")
        await message.channel.send("❌ **Processing failed!** No output file found.")

      os.remove(input_file_path)
      log(f"Finished `{attachment.filename}`.")

    except Exception as e:
      await message.add_reaction("⚠️")
      console.print(Panel.fit(f"Error: {e}", title="ERROR", style="bold red"))
      await message.channel.send(f"⚠️ **An error occurred:** `{str(e)}`")
      os.remove(input_file_path)

client.run(TOKEN)
