import discord
from discord.ext import commands
from discord import app_commands
import random

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="dice", description="🎲 Lancia i dadi e scommetti i tuoi Yen!")
    @app_commands.describe(scommessa="La quantità di Yen da scommettere", numero="Il numero su cui scommetti (da 1 a 6)")
    async def dice(self, interaction: discord.Interaction, scommessa: int, numero: int):
        if scommessa <= 0:
            return await interaction.response.send_message("❌ Devi scommettere una cifra valida maggiore di 0!", ephemeral=True)
        if numero < 1 or numero > 6:
            return await interaction.response.send_message("❌ Scegli un numero valido sul dado (da 1 a 6)!", ephemeral=True)

        user_id = interaction.user.id
        
        # Gestione scommessa (Passa in automatico se sei in God Mode)
        success = await self.bot.db.buy_item(user_id, scommessa)
        if not success:
            return await interaction.response.send_message("❌ Non hai abbastanza Yen per questa scommessa!", ephemeral=True)

        # Lancio del dado
        risultato = random.randint(1, 6)
        
        embed = discord.Embed(title="🎲 Il Dado Ruota sul Tavolo...", color=0x34495E)
        embed.set_thumbnail(url="https://i.imgur.com/9Xw5bZ8.png") # Icona dado generica o simile

        if risultato == numero:
            vincita = scommessa * 5
            await self.bot.db.add_coins(user_id, vincita)
            embed.title = "🎉 VITTORIA AL TAVOLO DELLE SCOMMESSE!"
            embed.description = f"Il dado si ferma sul numero **{risultato}**!\n\nHai indovinato alla perfezione! Il banco ti paga ben **{vincita} ¥**."
            embed.color = 0x2ECC71
        else:
            embed.title = "💸 Il banco vince questa volta..."
            embed.description = f"Il dado si ferma sul numero **{risultato}**.\n\nHai scelto il {numero}. Hai perso i tuoi **{scommessa} ¥**."
            embed.color = 0xE74C3C

        await interaction.response.send_message(embed=embed)


    @app_commands.command(name="blackjack", description="🃏 Sfida il banco dell'Izakaya a Blackjack!")
    @app_commands.describe(scommessa="La quantità di Yen da scommettere")
    async def blackjack(self, interaction: discord.Interaction, scommessa: int):
        if scommessa <= 0:
            return await interaction.response.send_message("❌ Devi scommettere una cifra valida maggiore di 0!", ephemeral=True)

        user_id = interaction.user.id
        
        # Controlla e scala i soldi (Gratis per i God Mode)
        success = await self.bot.db.buy_item(user_id, scommessa)
        if not success:
            return await interaction.response.send_message("❌ Non hai abbastanza Yen per questa scommessa!", ephemeral=True)

        # Funzione per calcolare il valore della mano
        def calcola_mano(mano):
            valore = 0
            assi = 0
            for carta in mano:
                if carta in ['J', 'Q', 'K']:
                    valore += 10
                elif carta == 'A':
                    valore += 11
                    assi += 1
                else:
                    valore += carta
            while valore > 21 and assi > 0:
                valore -= 10
                assi -= 1
            return valore

         mazzo = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A'] * 4
        random.shuffle(mazzo)

        mano_giocatore = [mazzo.pop(), mazzo.pop()]
        mano_banco = [mazzo.pop(), mazzo.pop()]

        # Vista interattiva con i pulsanti per Carta e Stai
        class BlackjackView(discord.ui.View):
            def __init__(self, db, god_modes):
                super().__init__(timeout=60)
                self.db = db
                self.god_modes = god_modes
                self.mano_g = mano_giocatore
                self.mano_b = mano_banco
                self.mazzo = mazzo
                self.finito = False

            async def genera_embed(self, titolo, colore, nascondi_banco=True):
                val_g = calcola_mano(self.mano_g)
                val_b = calcola_mano(self.mano_b)

                embed = discord.Embed(title=titolo, color=colore)
                embed.add_field(name="🃏 La tua Mano", value=f"Carte: {', '.join(map(str, self.mano_g))}\nValore: **{val_g}**", inline=True)
                
                if nascondi_banco:
                    embed.add_field(name="🏢 Mano del Banco", value=f"Carte: {self.mano_b[0]}, ❓\nValore: **?**", inline=True)
                else:
                    embed.add_field(name="🏢 Mano del Banco", value=f"Carte: {', '.join(map(str, self.mano_b))}\nValore: **{val_b}**", inline=True)
                
                embed.set_footer(text=f"Scommessa sul tavolo: {scommessa} ¥")
                return embed

            @discord.ui.button(label="Carta (Hit)", style=discord.ButtonStyle.green)
            async def hit(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
                if btn_interaction.user.id != interaction.user.id:
                    return await btn_interaction.response.send_message("❌ Questo tavolo da gioco non è tuo!", ephemeral=True)

                self.mano_g.append(self.mazzo.pop())
                val_g = calcola_mano(self.mano_g)

                if val_g > 21:
                    self.finito = True
                    self.stop()
                    embed = await self.genera_embed("💥 Sballato! Hai perso.", 0xE74C3C, nascondi_banco=False)
                    embed.description = f"Hai superato 21! Il banco si tiene i tuoi **{scommessa} ¥**."
                    await btn_interaction.response.edit_message(embed=embed, view=None)
                else:
                    embed = await self.genera_embed("🃏 Vuoi un'altra carta o ti fermi?", 0x3498DB)
                    await btn_interaction.response.edit_message(embed=embed, view=self)

            @discord.ui.button(label="Stai (Stand)", style=discord.ButtonStyle.red)
            async def stand(self, btn_interaction: discord.Interaction, button: discord.ui.Button):
                if btn_interaction.user.id != interaction.user.id:
                    return await btn_interaction.response.send_message("❌ Questo tavolo da gioco non è tuo!", ephemeral=True)

                self.finito = True
                self.stop()

                val_g = calcola_mano(self.mano_g)
                val_b = calcola_mano(self.mano_b)

                # Il banco pesca finché non arriva almeno a 17
                while val_b < 17:
                    self.mano_b.append(self.mazzo.pop())
                    val_b = calcola_mano(self.mano_b)

                embed = discord.Embed()
                # Calcolo vincitore
                if val_b > 21:
                    vincita = scommessa * 2
                    await self.db.add_coins(user_id, vincita)
                    embed = await self.genera_embed("🎉 Vittoria! Il banco ha sballato!", 0x2ECC71, nascondi_banco=False)
                    embed.description = f"Il banco ha superato 21! Ti porti a casa **{vincita} ¥**!"
                elif val_g > val_b:
                    vincita = scommessa * 2
                    await self.db.add_coins(user_id, vincita)
                    embed = await self.genera_embed("🎉 Vittoria! Hai battuto il banco!", 0x2ECC71, nascondi_banco=False)
                    embed.description = f"Il tuo punteggio è più alto! Guadagni **{vincita} ¥**."
                elif val_g < val_b:
                    embed = await self.genera_embed("💸 Il banco vince...", 0xE74C3C, nascondi_banco=False)
                    embed.description = f"Il banco ha fatto un punteggio migliore. Perdi i tuoi **{scommessa} ¥**."
                else:
                    # Pareggio (Push): restituisce la scommessa fatta
                    await self.db.add_coins(user_id, scommessa)
                    embed = await self.genera_embed("🤝 Pareggio (Push)!", 0xF1C40F, nascondi_banco=False)
                    embed.description = "Stesso punteggio! Il banco ti restituisce i tuoi Yen scommessi."

                await btn_interaction.response.edit_message(embed=embed, view=None)

            async def on_timeout(self):
                # Se l'utente scompare, perde la scommessa per abbandono
                if not self.finito:
                    try:
                        await interaction.edit_original_response(content="⏱️ Tempo scaduto! Hai abbandonato il tavolo e perso la scommessa.", view=None, embed=None)
                    except:
                        pass

        view = BlackjackView(self.bot.db, self.bot.db.GOD_MODES)
        
        # Controllo Blackjack immediato servito all'inizio
        if calcola_mano(mano_giocatore) == 21:
            vincita_bj = int(scommessa * 2.5)
            await self.bot.db.add_coins(user_id, vincita_bj)
            embed = await view.genera_embed("✨ NATURAL BLACKJACK! 🎉", 0x9B59B6, nascondi_banco=False)
            embed.description = f"Incredibile! Hai fatto Blackjack con le prime due carte! Il banco ti paga **{vincita_bj} ¥**."
            return await interaction.response.send_message(embed=embed)

        embed = await view.genera_embed("🃏 Tavolo da Blackjack dell'Izakaya", 0x3498DB)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Games(bot))