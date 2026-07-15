import discord
from discord.ext import commands
from discord import app_commands
import random

# Dizionario centralizzato del menu dell'Izakaya
MENU = {
    "ramen": {"name": "🍜 Ramen di Kyoto", "price": 120, "type": "cibo"},
    "sushi": {"name": "🍣 Set Sushi Deluxe", "price": 150, "type": "cibo"},
    "takoyaki": {"name": "🧆 Takoyaki (Polpettine di polpo)", "price": 60, "type": "cibo"},
    "gyoza": {"name": "🥟 Gyoza Grigliati", "price": 50, "type": "cibo"},
    "katsudon": {"name": "🍛 Katsudon (Cotoletta e riso)", "price": 110, "type": "cibo"},
    "mochi": {"name": "🍡 Mochi al Tè Verde", "price": 40, "type": "cibo"},
    # Bevande
    "sake": {"name": "🍶 Sake Caldo Pregiato", "price": 80, "type": "bevanda"},
    "corona": {"name": "🍺 Birra Corona extra", "price": 45, "type": "bevanda"},
    "asahi": {"name": "🍺 Birra Asahi Super Dry", "price": 50, "type": "bevanda"},
    "matcha": {"name": "🍵 Tè Verde Matcha Freddo", "price": 30, "type": "bevanda"},
    "ramune": {"name": "🥤 Ramune Originale", "price": 35, "type": "bevanda"}
}

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="wallet", description="👛 Controlla il saldo dei tuoi Yen nella taverna")
    @app_commands.describe(utente="L'utente di cui vuoi vedere il saldo (opzionale)")
    async def wallet(self, interaction: discord.Interaction, utente: discord.User = None):
        target = utente or interaction.user
        balance = await self.bot.db.get_balance(target.id)
        
        embed = discord.Embed(title="👛 Portafoglio dell'Izakaya", color=0xF1C40F)
        if balance >= 9999999:
            embed.description = f"**{target.name}** ha un conto bancario di cifre incalcolabili!\n💰 Saldo: **Infiniti ¥**"
        else:
            embed.description = f"Ecco le monete correnti di **{target.name}**:\n💰 Saldo: **{balance} ¥**"
            
        embed.set_thumbnail(url=target.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="give", description="🤝 Dona una parte dei tuoi Yen a un altro cliente")
    @app_commands.describe(utente="Il destinatario dei soldi", quantità="Quanti Yen vuoi donare")
    async def give(self, interaction: discord.Interaction, utente: discord.User, quantità: int):
        if quantità <= 0:
            return await interaction.response.send_message("❌ Devi specificare una cifra valida maggiore di 0!", ephemeral=True)
        if utente.id == interaction.user.id:
            return await interaction.response.send_message("❌ Non puoi donare soldi a te stesso!", ephemeral=True)
            
        sender_balance = await self.bot.db.get_balance(interaction.user.id)
        if sender_balance < quantità and interaction.user.id not in self.bot.db.GOD_MODES:
            return await interaction.response.send_message("❌ Non hai abbastanza Yen per fare questa donazione!", ephemeral=True)
            
        if interaction.user.id not in self.bot.db.GOD_MODES:
            with self.bot.db._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (quantità, interaction.user.id))
                conn.commit()
                
        await self.bot.db.add_coins(utente.id, quantità)
        await interaction.response.send_message(f"🤝 {interaction.user.mention} ha donato **{quantità} ¥** a {utente.mention}!")

    @app_commands.command(name="offri", description="🏮 Offri qualcosa dal menu a un altro utente al tavolo!")
    @app_commands.describe(utente="L'utente a cui vuoi offrire", oggetto="L'ID del piatto o bevanda (es. ramen, corona)")
    async def offri(self, interaction: discord.Interaction, utente: discord.User, oggetto: str):
        oggetto = oggetto.lower().strip()
        if oggetto not in MENU:
            return await interaction.response.send_message("❌ Questo piatto non è sul menu. Guarda `/menu`!", ephemeral=True)
            
        if utente.id == interaction.user.id:
            return await interaction.response.send_message("❌ Non puoi offrire qualcosa a te stesso, usa `/buy` e poi `/eat`!", ephemeral=True)
            
        item = MENU[oggetto]
        user_id = interaction.user.id
        
        success = await self.bot.db.buy_item(user_id, item['price'])
        if not success:
            return await interaction.response.send_message(f"❌ Non hai abbastanza soldi per offrire un {item['name']} ({item['price']} ¥)!", ephemeral=True)
            
        azione = "ha offerto una ciotola fumante di" if item['type'] == "cibo" else "ha pagato un bel giro di"
        embed = discord.Embed(
            title="🏮 Un regalo al tavolo! ✨",
            description=f"🌸 {interaction.user.mention} {azione} **{item['name']}** a {utente.mention}!\n\n*Si sente un caloroso 'Kanpai!' echeggiare nella taverna!*",
            color=0x9B59B6
        )
        embed.set_footer(text="Che generosità! Il bancone ringrazia.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="daily", description="💰 Svolgi il tuo turno giornaliero e ricevi una paga casuale da 0 a 500 ¥!")
    async def daily(self, interaction: discord.Interaction):
        can_claim = await self.bot.db.check_and_set_daily(interaction.user.id)
        if not can_claim:
            return await interaction.response.send_message("🏮 Per oggi hai già dato! Il proprietario ti ha già pagato. Torna domani!", ephemeral=True)
        
        guadagno = random.randint(0, 500)
        await self.bot.db.add_coins(interaction.user.id, guadagno)
        
        embed = discord.Embed(
            title="🏮 Turno di Lavoro Completato!",
            description=f"Hai aiutato a pulire i tavoli e a servire i clienti ai banconi!\nIl proprietario ti allunga la tua paga di **{guadagno} ¥**.",
            color=0x2ECC71
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="menu", description="📜 Sfoglia la lista dei piatti e delle bevande dell'Izakaya")
    async def menu(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🏮 MENU DELL'IZAKAYA 🏮", color=0xF39C12)
        cibi_text = ""
        bevande_text = ""
        
        for item_id, info in MENU.items():
            line = f"`/{item_id}` — **{info['name']}**: {info['price']} ¥\n"
            if info['type'] == "cibo":
                cibi_text += line
            else:
                bevande_text += line
                
        embed.add_field(name="🍱 Piatti Tipici Giapponesi", value=cibi_text, inline=False)
        embed.add_field(name="🍶 Bevande & Birre", value=bevande_text, inline=False)
        embed.set_footer(text="Usa /buy <id_piatto> per lo zaino o /offri per regalarlo!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buy", description="🛍️ Ordina qualcosa dal menu e mettilo nel tuo zaino")
    @app_commands.describe(oggetto="L'ID del piatto o bevanda da comprare (es. ramen, corona)")
    async def buy(self, interaction: discord.Interaction, oggetto: str):
        oggetto = oggetto.lower().strip()
        if oggetto not in MENU:
            return await interaction.response.send_message("❌ Questo piatto non è sul nostro menu.", ephemeral=True)
            
        item = MENU[oggetto]
        user_id = interaction.user.id
        success = await self.bot.db.buy_item(user_id, item['price'])
        
        if not success:
            return await interaction.response.send_message("❌ Non hai abbastanza Yen!", ephemeral=True)
            
        await self.bot.db.add_to_inventory(user_id, oggetto, item['name'])
        await interaction.response.send_message(f"🛍️ Hai acquistato **{item['name']}** per {item['price']} ¥! È stato messo nel tuo zaino (`/bag`).")

    @app_commands.command(name="bag", description="🎒 Apri il tuo zaino per vedere il cibo e le bevande che possiedi")
    async def bag(self, interaction: discord.Interaction):
        items = await self.bot.db.get_inventory(interaction.user.id)
        if not items:
            return await interaction.response.send_message("🎒 Il tuo zaino è completamente vuoto.", ephemeral=True)
            
        embed = discord.Embed(title=f"🎒 Zaino di {interaction.user.name}", color=0x3498DB)
        desc = "Ecco le provviste che hai acquistato nella taverna:\n\n"
        for item_id, item_name, qty in items:
            desc += f"• **{item_name}** (ID: `{item_id}`) — x{qty}\n"
        desc += "\n*Puoi consumarli in qualsiasi momento digitando `/eat <id_oggetto>`!*"
        embed.description = desc
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="eat", description="😋 Mangia o bevi un oggetto presente nel tuo zaino")
    @app_commands.describe(oggetto="L'ID dell'oggetto da consumare (es. ramen, corona)")
    async def eat(self, interaction: discord.Interaction, oggetto: str):
        oggetto = oggetto.lower().strip()
        if oggetto not in MENU:
            return await interaction.response.send_message("❌ Questo oggetto non esiste sul menu.", ephemeral=True)
            
        user_id = interaction.user.id
        item = MENU[oggetto]
        removed = await self.bot.db.remove_one_from_inventory(user_id, oggetto)
        
        if not removed:
            return await interaction.response.send_message(f"❌ Non hai nessun **{item['name']}** nel tuo zaino!", ephemeral=True)
            
        azione = "ha gustato" if item['type'] == "cibo" else "ha bevuto tutto d'un fiato"
        await interaction.response.send_message(f"😋 {interaction.user.mention} {azione} un delizioso **{item['name']}** al bancone dell'Izakaya! Oishii!")

async def setup(bot):
    await bot.add_cog(Economy(bot))