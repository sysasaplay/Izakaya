import os
import asyncio
import sys
import discord
from discord.ext import commands
from database import IzakayaDB

# ─── CONFIGURAZIONE TOKEN ──────────────────────────────────────────
# Incolla il tuo token reale tra le virgolette qui sotto.
# Esempio: TOKEN = "MTB5NDk3...ecc..."
TOKEN = "TOKEN_BOT_DISCORD"
# ───────────────────────────────────────────────────────────────────

# Controllo di sicurezza immediato per evitare che si avvii vuoto
if TOKEN == "INCOLLA_QUI_IL_TUO_TOKEN_DI_DISCORD" or not TOKEN:
    print("❌ ERRORE: Non hai inserito il tuo vero Token di Discord alla riga 11!")
    print("Sostituisci la scritta tra virgolette con il codice segreto del tuo bot.")
    sys.exit(1)

class IzakayaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)
        self.db = IzakayaDB()

    async def setup_hook(self):
        # Inizializza il database SQLite locale
        self.db.setup()
        print("✅ Tabelle database inizializzate su: izakaya.db")

        # Carica i moduli (Cogs) della taverna
        initial_extensions = ["cogs.economy", "cogs.menu", "cogs.games", "cogs.bump", "cogs.admin"]
        for ext in initial_extensions:
            try:
                await self.load_extension(ext)
                print(f"📦 Caricato con successo: {ext}")
            except Exception as e:
                print(f"❌ Errore nel caricamento di {ext}: {e}")

    async def on_ready(self):
        print("\n" + "="*40)
        print(f"🏮 {self.user.name} è online e pronto a servire i clienti!")
        print(f"🆔 ID Bot: {self.user.id}")
        print("="*40 + "\n")
        
        # Sincronizza i comandi slash globalmente su Discord
        print("🔄 Sincronizzazione dei comandi slash in corso...")
        await self.tree.sync()
        print("✨ Comandi slash sincronizzati ovunque!")

async def main():
    bot = IzakayaBot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🏮 L'Izakaya chiude i battenti. Alla prossima!")
