import discord
from discord.ext import commands
import asyncio

class Bump(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # 1. Controlla se il messaggio proviene dal Bot ufficiale di Disboard (ID: 302050872383242240)
        if message.author.id == 302050872383242240:
            
            # 2. Controlla se Disboard ha inviato un Embed (la sua classica risposta di successo)
            if message.embeds:
                embed = message.embeds[0]
                desc = embed.description or ""
                
                # Disboard di solito risponde con "Bump done!" o "Bump completato!" nel testo dell'embed
                if "Bump done" in desc or "Bump completato" in desc or "👍" in desc:
                    
                    # 3. Trova l'utente che ha eseguito il comando analizzando l'interazione o i tag vicini
                    # Se l'embed menziona l'utente o se è un'interazione diretta, prendiamo il suo ID
                    user_to_mention = None
                    if message.interaction:
                        user_to_mention = message.interaction.user.mention
                    else:
                        # Fallback: se non c'è l'oggetto interaction, usa @here per sicurezza
                        user_to_mention = "@here"

                    # Conferma immediata nella chat che l'Izakaya ha registrato il bump
                    await message.channel.send(
                        f"🏮 **Izakaya Logger:** Bump di Disboard rilevato! Sveglia impostata per {user_to_mention}. Ci rivediamo tra **2 ore**!"
                    )

                    # 4. Avvia il timer in background (7200 secondi = 2 ore)
                    self.bot.loop.create_task(self.remind_bump(message.channel.id, user_to_mention))

    async def remind_bump(self, channel_id, user_mention):
        # Attende esattamente 2 ore
        await asyncio.sleep(7200)
        
        channel = self.bot.get_channel(channel_id)
        if channel:
            embed = discord.Embed(
                title="🏮 Orario del Bump! — 💥",
                description=f"Sono passate **2 ore** dall'ultimo bump di Disboard!\n{user_mention}, usa di nuovo `/bump` per portare nuovi clienti in taverna!",
                color=0xFF4500
            )
            embed.set_footer(text="Disboard è pronto per un altro giro!")
            
            # Invia il promemoria taggando l'utente specifico
            await channel.send(content=f"🔔 {user_mention}", embed=embed)

async def setup(bot):
    await bot.add_cog(Bump(bot))