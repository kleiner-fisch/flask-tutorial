

import sqlalchemy
import pdb

from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine

def init_db():
    engine = create_engine("sqlite+pysqlite:///battle_line.db", echo=True)

    metadata_obj = MetaData()

    user_table = Table(
        "user_account",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("name", String(30),unique=True, nullable=False),
        Column("password", String(30), nullable=False),
        Column("mail_address", String, nullable=False),
    )

    # has the cards of the lines
    line_card_table = Table(
        "line_card",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("pid",Integer, ForeignKey("user_account.id"), nullable=False),    
        Column("line_id",Integer, ForeignKey("line.id"), nullable=False),       
        Column("card", Integer, nullable=False),
    )

    line_table = Table(
        "line",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        # number from 0 to 8
        Column("line_number", Integer, nullable=False),
        Column("game_id", Integer, ForeignKey("game.id"),nullable=False),
        Column("has_winner", Boolean, nullable=False),
        Column("winner", Integer, ForeignKey("user_account.id"), nullable=True),
    )

    hand_card_table = Table(
        "hand_card",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("game_id", Integer, ForeignKey("game.id"),nullable=False),
        Column("pid",Integer, ForeignKey("user_account.id"), nullable=False),    
        Column("card", Integer, nullable=False),
    )


    game_table = Table(
        "game",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("p1_pid", ForeignKey("user_account.id"), nullable=False),    
        Column("p2_pid", ForeignKey("user_account.id"), nullable=False),    
        # True if p1 is current player, False if p2 is current player
        Column("p1_is_current_player", Boolean, nullable=False),    
        #
        # Claim
        Column("p1_has_claim", Boolean, nullable=False),
        Column("p2_has_claim", Boolean, nullable=False),
        Column("claimed_line_id", Integer, nullable=True),
        #
        Column("unresolved_scout", Boolean, nullable=False),
        #
        # public cards
        Column("public_card_1", Integer, nullable=True),
        Column("public_card_2", Integer, nullable=True),
        #
        # winner
        Column("game_finished", Boolean, nullable=False),
        Column("p1_is_winning_player", Boolean, nullable=True),
    )

    metadata_obj.create_all(engine)
