import discord
from discord.ext import commands
from discord import app_commands
import random

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="wallet", description="👛 Controlla quanti Yen hai in tasca")
    async def wallet(self, interaction: discord.Interaction):
        balance = await self.bot.db.get_balance(interaction.user.id)
        embed = discord.Embed(
            title="👛 Il tuo Portafoglio",
            description=f"Al momento possiedi: **{balance} ¥**",
            color=0x2ECC71
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="work", description="🧹 Lavora nell'Izakaya per guadagnare Yen")
    async def work(self, interaction: discord.Interaction):
        paga = random.randint(30, 100)
        lavori = [
            "Hai lavato i piatti nel retrobottega.",
            "Hai servito ai tavoli un gruppo di avventori allegri.",
            "Hai pulito il bancone di legno.",
            "Hai aiutato lo chef a preparare i ramen."
        ]
        await self.bot.db.add_coins(interaction.user.id, paga)
        await interaction.response.send_message(f"🧹 {random.choice(lavori)} Guadagni **{paga} ¥**.")

async def setup(bot):
    await bot.add_cog(Economy(bot))
