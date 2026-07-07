import discord
from discord.ext import commands
from discord import app_commands
import menu_data

class Menu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="menu", description="📜 Visualizza il menu dell'izakaya")
    async def menu(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🏮 Izakaya no Menu — 居酒屋のメニュー", color=0xFF4500)
        embed.description = "Benvenuto! Ecco cosa serviamo stasera.\nUsa `/buy [chiave]` per ordinare o `/offer [chiave] @utente` per offrire!"

        categories = {}
        for key, info in menu_data.MENU.items():
            cat = info['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(f"{info['emoji']} {info['label']} — {info['price']} ¥ • chiave: `{key}`")

        for cat, items in categories.items():
            embed.add_field(name=cat, value="\n".join(items), inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buy", description="🛒 Compra qualcosa per te")
    @app_commands.describe(chiave="La chiave dell'item da comprare (es. ramen)")
    async def buy(self, interaction: discord.Interaction, chiave: str):
        item = menu_data.get_item(chiave)
        if not item:
            return await interaction.response.send_message("❌ Item non trovato! Controlla il `/menu`.", ephemeral=True)
        
        success = await self.bot.db.buy_item(interaction.user.id, item['price'])
        if not success:
            return await interaction.response.send_message("❌ Saldo insufficiente!", ephemeral=True)
            
        await interaction.response.send_message(f"🛒 Hai ordinato un {item['label']} {item['emoji']}!")

    @app_commands.command(name="offer", description="🎁 Offri qualcosa a un altro utente")
    @app_commands.describe(chiave="Chiave dell'item", utente="L'utente a cui offrire")
    async def offer(self, interaction: discord.Interaction, chiave: str, utente: discord.Member):
        item = menu_data.get_item(chiave)
        if not item:
            return await interaction.response.send_message("❌ Item non trovato!", ephemeral=True)

        if not await self.bot.db.buy_item(interaction.user.id, item['price']):
            return await interaction.response.send_message("❌ Non hai abbastanza Yen per questo gesto!", ephemeral=True)

        await interaction.response.send_message(f"🎁 {interaction.user.mention} ha offerto {item['emoji']} **{item['label']}** a {utente.mention}!")

    @app_commands.command(name="round", description="🍻 Offri un giro a tutti i presenti nel tuo canale vocale!")
    async def round(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            return await interaction.response.send_message("❌ Devi essere in un canale vocale per offrire un giro!", ephemeral=True)

        members = [m for m in interaction.user.voice.channel.members if not m.bot]
        costo_unitario = 100 
        costo_totale = costo_unitario * len(members)

        if not await self.bot.db.buy_item(interaction.user.id, costo_totale):
            return await interaction.response.send_message(f"❌ Ti servono {costo_totale} ¥ per offrire a tutti.", ephemeral=True)

        nomi = ", ".join([m.display_name for m in members])
        await interaction.response.send_message(f"🍻 {interaction.user.mention} offre un giro di Sake a: {nomi}!")

    @buy.autocomplete("chiave")
    @offer.autocomplete("chiave")
    async def item_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=val['label'], value=key)
            for key, val in menu_data.MENU.items()
            if current.lower() in key.lower()
        ][:25]

async def setup(bot):
    await bot.add_cog(Menu(bot))
