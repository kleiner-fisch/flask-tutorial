import sqlalchemy
import pdb
from .game import Game 
from .line import Line
from . import game_controller
from flask import current_app, g
import click


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


def get_db():
    if 'db' not in g:
        g.db = DB_Wrapper()
    return g.db



def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')




class DB_Wrapper:


    def __init__(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

        self.metadata_obj = MetaData()

        self.user_table = Table(
            "user_account",
            self.metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("name", String(30), nullable=False),
            Column("mail_address", String, nullable=False),
        )

        # has the cards of the lines
        self.line_card_table = Table(
            "line_card",
            self.metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("pid",Integer, ForeignKey("user_account.id"), nullable=False),    
            Column("line_id",Integer, ForeignKey("line.id"), nullable=False),       
            Column("card", Integer, nullable=False),
        )

        self.line_table = Table(
            "line",
            self.metadata_obj,
            Column("id", Integer, primary_key=True),
            # number from 0 to 8
            Column("line_number", Integer, nullable=False),
            Column("game_id", Integer, ForeignKey("game.id"),nullable=False),
            Column("has_winner", Boolean, nullable=False),
            Column("winner", Integer, ForeignKey("user_account.id"), nullable=True),
        )

        self.hand_card_table = Table(
            "hand_card",
            self.metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("game_id", Integer, ForeignKey("game.id"),nullable=False),
            Column("pid",Integer, ForeignKey("user_account.id"), nullable=False),    
            Column("card", Integer, nullable=False),
        )


        self.game_table = Table(
            "game",
            self.metadata_obj,
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

        self.metadata_obj.create_all(self.engine)

    def close(self):
        pass


    def get_game(self, game_id):
        '''gets the game with the given <game_id> from the database and assembles the data into a game object and returns it'''
        game_stmt = sqlalchemy.select(self.game_table).where(self.game_table.c.id == game_id)
        hand_cards_stmt = sqlalchemy.select(self.hand_card_table).where(self.hand_card_table.c.game_id == game_id)
        lines_stmt = sqlalchemy.select(self.line_table).where(self.line_table.c.game_id == game_id)
        line_cards_stmt = lambda line_id: \
            sqlalchemy.select(self.line_card_table).where(self.line_card_table.c.line_id == line_id)
        with self.engine.begin() as conn:
            game_result = conn.execute(game_stmt).one()
            hand_p1, hand_p2 = self.parse_hands(conn.execute(hand_cards_stmt), 
                                        game_result.p1_pid, game_result.p2_pid)
            lines_result = conn.execute(lines_stmt)
            lines = [self.parse_line(conn.execute(line_cards_stmt(row.id ), 
                                            game_result.p1_pid, game_result.p2_pid))
                                            for row in lines_result]
            game = Game(game_result.p1_pid, game_result.p2_pid, game_result.id,
                    p0_hand=hand_p1, p1_hand=hand_p2,
                        lines=lines)
            return game

    def parse_hands(self, db_result, p1_pid, p2_pid):
        '''extracts the cards of the hands and partitions them into p1 and p2 players cards'''
        cards = [(row.card, row.pid) for row in db_result]
        p1_hands = [c for (c, pid) in cards if pid == p1_pid]
        p2_hands = [c for (c, pid) in cards if pid == p2_pid]
        return (p1_hands, p2_hands)

    def parse_line(self, db_result, p1_pid, p2_pid):
        '''extracts the cards of the battle lines and assembles them into objects'''
        result = Line(p1_pid, p2_pid)
        result.sides[p1_pid] += [row.card for row in db_result if row.pid == p1_pid]
        result.sides[p2_pid] += [row.card for row in db_result if row.pid == p2_pid]
        return result



    def create_game(self, player_id1, player_id2, starting_player=None):
        '''creates a new game with the specified players and returns the id of the created game.
        If no starting player is given one is choosen randomly'''
        game = game_controller.create_game(player_id1, player_id2, starting_player)
        new_game_id = None                                   
        with self.engine.begin() as conn:
            result = conn.execute(sqlalchemy.insert(self.game_table),
            {
                "p1_pid" : game.p0, "p2_pid" : game.p1, "p1_is_current_player" : game.current_player==game.p0,
                "p1_has_claim" :False, "p2_has_claim" : False,
                "unresolved_scout" : False, "game_finished" : False, 
            })
            #pdb.set_trace()
            new_game_id = result.inserted_primary_key.id
            cards_p1 = [{"game_id" : new_game_id, "pid" : game.p0, "card" : c} for c in game.hands[game.p0]]
            cards_p2 = [{"game_id" : new_game_id, "pid" : game.p1, "card" : c} for c in game.hands[game.p1]]

            conn.execute(sqlalchemy.insert(self.hand_card_table), cards_p1)
            conn.execute(sqlalchemy.insert(self.hand_card_table), cards_p2)

            conn.commit()
            return new_game_id
    