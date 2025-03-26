import discord
from discord import app_commands
from discord.ext import commands
from database.db_manager import DatabaseManager
from bot import is_admin

class Set_Category(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db_manager = None
    
    async def ensure_db_manager(self, interaction: discord.Interaction):
        """Ensure that db_manager is initialized for the current guild"""
        guild_id = interaction.guild.id
        guild_name = interaction.guild.name
        
        if (self.db_manager is None or 
            self.db_manager.guild_id != guild_id):
            self.db_manager = DatabaseManager(guild_id, guild_name)
            await self.db_manager.init_db()
            self.application_category_id = await self.db_manager.get_application_category()
        return self.db_manager
    
    @app_commands.command(name="set_category", description="設置申請頻道的類別")
    @is_admin()
    async def set_application_category(self, interaction: discord.Interaction, category: discord.CategoryChannel = None):
        """Set the category for application channels"""
        await self.ensure_db_manager(interaction)
        
        if category:
            self.application_category_id = category.id
            await self.db_manager.save_application_category(category.id)
            embed = discord.Embed(
                title="設置成功",
                description=f"已將申請頻道類別設為 '{category.name}'",
                color=discord.Color.green()
            )
            
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="set_current_category", description="將當前頻道的類別設置為申請頻道類別")
    @is_admin()
    async def set_current_category(self, interaction: discord.Interaction):
        """Set the current channel's category as the application category"""
        await self.ensure_db_manager(interaction)
        
        if not interaction.channel.category:
            embed = discord.Embed(
                title="無法設置",
                description="當前頻道沒有所屬類別。請先將頻道放入一個類別中，或使用 `/set_category` 命令指定類別。",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        category = interaction.channel.category
        self.application_category_id = category.id
        await self.db_manager.save_application_category(category.id)
        
        embed = discord.Embed(
            title="設置成功",
            description=f"已將申請頻道類別設為 '{category.name}'",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Set_Category(bot))