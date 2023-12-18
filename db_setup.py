
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine


# The card integers refer to positions in the following sequence of card names:
#
# A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, 
# B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, 
# C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, 
# D1, D2, D3, D4, D5, D6, D7, D8, D9, D10, 
# E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, 
# F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, 
# ALEXANDER, DARIUS, CAVALRY, SHIELD_BEARER, FOG, MUD, SCOUT, REDEPLOY, DESERTER, TRAITOR


engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

metadata_obj = MetaData()

user_table = Table(
    "user_account",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(30), nullable=False),
    Column("mail_address", String, nullable=False),
)

# has the cards of the lines
line_cards_table = Table(
    "line_cards",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    # number from 1 to 9
    Column("line_id", Integer, nullable=False),
    Column("game_id", Integer, ForeignKey("current_games.id"),nullable=False),
    Column("pid",Integer, ForeignKey("user_account.id"), nullable=False),    
    Column("card", Integer, nullable=False),
)


hand_cards_table = Table(
    "hand_cards",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("game_id", Integer, ForeignKey("current_games.id"),nullable=False),
    Column("pid",Integer, ForeignKey("user_account.id"), nullable=False),    
    Column("card", Integer, nullable=False),
)



#### TODO Look up how to define this database! ERP design.. 1-to-n or m-n relationships...

game_table = Table(
    "current_games",
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