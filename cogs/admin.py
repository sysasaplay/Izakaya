import discord
from discord.ext import commands
from discord import app_commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # ID protetti (Tu e Ally non potete essere bannati dal bot)
        self.IMMUNE_IDS = [876853397746225162, 1363915831091921098]

    @app_commands.command(name="ban", description="🔨 Bandisci un utente molesto dall'Izakaya")
    @app_commands.describe(utente="L'utente da bannare", motivo="Il motivo del ban")
    # Questo controllo fa sì che solo chi ha il permesso "Administrator" su Discord possa vedere e usare il comando
    @app_commands.default_permissions(administrator=True)
    async def ban(self, interaction: discord.Interaction, utente: discord.Member, motivo: str = "Nessun motivo specificato"):
        
        # Controllo di sicurezza: non puoi bannare te stesso
        if utente.id == interaction.user.id:
            return await interaction.response.send_message("❌ Non puoi cacciarti da solo dalla tua stessa taverna!", ephemeral=True)

        # Controllo Immunità (God Mode per te e Ally)
        if utente.id in self.IMMUNE_IDS:
            return await interaction.response.send_message("🔰 Questo utente è un ospite d'onore dell'Izakaya, non può essere bannato!", ephemeral=True)

        try:
            # Esegue il ban effettivo su Discord (cancella anche i messaggi degli ultimi 7 giorni)
            await utente.ban(delete_message_days=7, reason=motivo)
            
            # Crea un embed d'effetto per annunciare il ban nel canale
            embed = discord.Embed(
                title="🔨 L'Izakaya ha un cliente in meno!",
                description=f"{utente.mention} è stato bandito permanentemente dal server.",
                color=0xE74C3C
            )
            embed.add_field(name="👤 Bandito da", value=interaction.user.mention, inline=True)
            embed.add_field(name="📝 Motivo", value=motivo, inline=True)
            embed.set_thumbnail(url=utente.display_avatar.url)
            embed.set_footer(text="Il rispetto delle regole viene prima di tutto nella taverna.")
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ Non ho i permessi necessari per bannare questo utente. Controlla che il mio ruolo sia più in alto del suo nella lista dei ruoli del server!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Si è verificato un errore: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))
