import sqlalchemy
import pdb
from .game import Game 
from .line import Line
from . import game_controller
from flask import current_app, g
import click
from .user import User


from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String, Boolean
from sqlalchemy import ForeignKey, bindparam
from sqlalchemy import create_engine

from flask import current_app

from werkzeug.security import check_password_hash, generate_password_hash


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

class DB_Wrapper:


    def __init__(self):
        # TODO currently these tables are created for every request, instead of always using the same DB_Wrapper object. 
        #   Not sure if this is expensive
        #pdb.set_trace()
        url= "sqlite+pysqlite:///" + current_app.config['DATABASE_URL']
        echo=current_app.config.get('DATABASE_ECHO', True)
        self.engine = create_engine(url, echo=echo)

#        self.engine = create_engine("sqlite+pysqlite:///battle_line.db", echo=True)

        self.metadata_obj = MetaData()

        self.user_table = Table(
            "user_account",
            self.metadata_obj,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("name", String(30),unique=True, nullable=False),
            Column("mail_address", String, nullable=False),
            Column("password", String, nullable=False),
        )

        # has the cards of the lines
        self.line_card_table = Table(
            "line_card",
            self.metadata_obj,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("pid",Integer, ForeignKey("user_account.id"), nullable=False),    
            Column("line_id",Integer, ForeignKey("line.id"), nullable=False),       
            Column("card", Integer, nullable=False),
        )

        self.line_table = Table(
            "line",
            self.metadata_obj,
            Column("id", Integer, primary_key=True, autoincrement=True),
            # number from 0 to 8
            Column("line_number", Integer, nullable=False),
            Column("game_id", Integer, ForeignKey("game.id"),nullable=False),
            Column("has_winner", Boolean, nullable=False),
            Column("winner", Integer, ForeignKey("user_account.id"), nullable=True),
        )

        self.hand_card_table = Table(
            "hand_card",
            self.metadata_obj,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("game_id", Integer, ForeignKey("game.id"),nullable=False),
            Column("pid",Integer, ForeignKey("user_account.id"), nullable=False),    
            Column("card", Integer, nullable=False),
        )


        self.game_table = Table(
            "game",
            self.metadata_obj,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("p1_pid", ForeignKey("user_account.id"), nullable=False),    
            Column("p2_pid", ForeignKey("user_account.id"), nullable=False),    
            Column("current_player", ForeignKey("user_account.id"), nullable=False),    
            #
            # Claim
            Column("p1_has_claim", Boolean, nullable=False),
            Column("p2_has_claim", Boolean, nullable=False),
            Column("claimed_line_number", Integer, nullable=True),
            #
            Column("unresolved_scout", Boolean, nullable=False),
            #
            # public cards
            Column("public_card_1", Integer, nullable=True),
            Column("public_card_2", Integer, nullable=True),
            #
            # winner
            Column("game_finished", Boolean, nullable=False),
            Column("winning_player", ForeignKey("user_account.id"), nullable=True),
        )

        self.metadata_obj.create_all(self.engine, checkfirst=True)



    def get_game(self, game_id):
        '''gets the game with the given <game_id> from the database and assembles the data into a game object and returns it'''
        game_stmt = sqlalchemy.select(self.game_table).where(self.game_table.c.id == game_id)
        hand_cards_stmt = sqlalchemy.select(self.hand_card_table).where(self.hand_card_table.c.game_id == game_id)
        with self.engine.begin() as conn:
            game_result = conn.execute(game_stmt).one()
            hand_p1, hand_p2 = self.parse_hands(conn.execute(hand_cards_stmt), 
                                        game_result.p1_pid, game_result.p2_pid)
            lines = self.load_lines(game_id, game_result.p1_pid, game_result.p2_pid, conn)
            if game_result.p1_has_claim:
                claim = {'player_id' : game_result.p1_pid, 'line_number':game_result.claimed_line_number }
                pass
            elif game_result.p2_has_claim:
                claim = {'player_id' : game_result.p2_pid, 'line_number':game_result.claimed_line_number }
            else:
                claim=dict()
            game = Game(game_id=game_result.id, p1=game_result.p1_pid, p2=game_result.p2_pid, current_player=game_result.current_player,
                    p1_hand=hand_p1, p2_hand=hand_p2, claim=claim,
                        lines=lines, unresolved_scout=game_result.unresolved_scout)
            # TODO here we should also load the winner, whether scout is open and open claims
            return game

    def parse_hands(self, db_result, p1_pid, p2_pid):
        '''extracts the cards of the hands and partitions them into p1 and p2 players cards'''
        cards = [(row.card, row.pid) for row in db_result]
        p1_hands = [c for (c, pid) in cards if pid == p1_pid]
        p2_hands = [c for (c, pid) in cards if pid == p2_pid]
        return (p1_hands, p2_hands)
    
    def load_lines(self, game_id, p1_pid, p2_pid, conn):
        '''loads the lines for the game_id and parses them into objects'''
        # first we load and initialize the lines
        get_lines_stmt = sqlalchemy.select(self.line_table)\
            .where(self.line_table.c.game_id == game_id)
        lines_result = conn.execute(get_lines_stmt)
        lines = [None]*9
        for row in lines_result:
            lines[row.line_number]= Line(sides={p1_pid:[], p2_pid:[]}, id=row.id, won_by=row.winner)
        # then we load the cards ... 
        stmt = sqlalchemy.select(self.line_table, self.line_card_table)\
                .join(self.line_card_table, self.line_table.c.id == self.line_card_table.c.line_id)\
                .where( self.line_table.c.game_id == game_id)
        result = conn.execute(stmt)
        # ... and add them to the lines
        for row in result:
            line = lines[row.line_number] 
            line.sides[row.pid].append(row.card)
        assert lines.count(None) == 0, 'unexpected lines result: {}'.format(lines)
        return lines

    def create_game(self, player_id1, player_id2, starting_player=None):
        '''creates a new game with the specified players and returns the id of the created game.
        If no starting player is given one is choosen randomly'''
        game = game_controller.create_game(player_id1, player_id2, starting_player)
        with self.engine.begin() as conn:
            result = conn.execute(sqlalchemy.insert(self.game_table),
            {
                "p1_pid" : game.p1, "p2_pid" : game.p2, "current_player" : game.current_player,
                "p1_has_claim" :False, "p2_has_claim" : False,
                "unresolved_scout" : False, "game_finished" : False, 
            })
            game.game_id = result.inserted_primary_key.id

            stmt, values = self.insert_lines_stmt(game)
            conn.execute(stmt, values)

            stmt, values = self.insert_hand_cards_stmt(game)
            conn.execute(stmt, values)

            conn.commit()
            return game.game_id
        
    def store_game(self, game):
       with self.engine.begin() as conn:
            stmt = sqlalchemy.update(self.game_table).where(self.game_table.c.id == game.game_id)
            claim_pid = game.claim.get('player_id', None)
            result = conn.execute(stmt,
            {
                "p1_pid" : game.p1, "p2_pid" : game.p2, "current_player" : game.current_player,
                "p1_has_claim" : claim_pid == game.p1, "p2_has_claim" : claim_pid == game.p2,
                "claimed_line_number" : game.claim.get('line_number', None),
                "unresolved_scout" : game.unresolved_scout, 
                "game_finished" : game.winner is None, "winning_player" : game.winner
            })
            # HAND CARDS

            # remove old hand cards
            conn.execute(sqlalchemy.delete(self.hand_card_table)\
                         .where(self.hand_card_table.c.game_id == game.game_id))
       
            # insert current hand cards. 
            stmt, values = self.insert_hand_cards_stmt(game)
            # we check whether list is empty, as for an empty list 
            # apparently a row with default values is inserted..
            if values: conn.execute(stmt, values)

            # LINES
            # we remove all existing cards of lines (as some cards may have been moved) ... 
            # in our game object cards don't have IDs, hence we need to work to find out the cards to delete
            get_line_cards_stmt = sqlalchemy.select(self.line_card_table) \
                .join(self.line_table) \
                .where(self.line_table.c.game_id == game.game_id)
            result = conn.execute(get_line_cards_stmt)
            line_card_ids = [{'bound_line_id': row.id} for row in result]
            if line_card_ids:
                conn.execute(sqlalchemy.delete(self.line_card_table)\
                    .where(self.line_card_table.c.id == bindparam('bound_line_id')),
                    line_card_ids)

            # ... and add the cards of the lines
            stmt, values = self.insert_line_cards_stmt(game)
            if values: conn.execute(stmt, values)
 
            # We update whether lines are won by placers
            stmt, values = self.update_lines_stmt(game)
            if values: conn.execute(stmt, values)

            conn.commit()

    def insert_lines_stmt(self, game):
        lines = [{'line_number': index, 'game_id': game.game_id, 
                  'has_winner': line.won_by != None, 'winner': line.won_by} 
                  for index, line in enumerate(game.lines)]
        return sqlalchemy.insert(self.line_table), lines


    def insert_line_cards_stmt(self, game):
        line_cards = lambda pid: [{"line_id": line.id, "pid" : pid, "card" : c} 
                    for line in game.lines for c in line.sides[pid]]
        line_cards = sum([line_cards(pid) for pid in [game.p1, game.p2]], [])
        return sqlalchemy.insert(self.line_card_table), line_cards


    def update_lines_stmt(self, game):
        lines = [{"bound_line_number": line_number, "new_has_winner" : line.won_by != None,
                        "new_winner" : line.won_by} for line_number, line in enumerate(game.lines)]

        line_update = sqlalchemy.update(self.line_table)\
            .where(self.line_table.c.game_id == game.game_id) \
            .where(self.line_table.c.line_number == bindparam("bound_line_number")) \
            .values(has_winner=bindparam("new_has_winner"), winner=bindparam("new_winner"))
        return line_update, lines
    

    def insert_hand_cards_stmt(self, game):
        '''creates an insert statement for the hand cards and collects the values to insert'''
        hand_cards_p1 = [{"game_id" : game.game_id, "pid" : game.p1, "card" : c} for c in game.hands[game.p1]]
        hand_cards_p2 = [{"game_id" : game.game_id, "pid" : game.p2, "card" : c} for c in game.hands[game.p2]]
        return sqlalchemy.insert(self.hand_card_table), hand_cards_p1 + hand_cards_p2


    def create_user(self, username, password, mail):
        '''creates a nuser with the given data'''
        hashed_pw = generate_password_hash(password)
        new_user_id = None                                   
        with self.engine.begin() as conn:
            result = conn.execute(sqlalchemy.insert(self.user_table),
            {
                "name" : username, "password" : hashed_pw, "mail_address" : mail
            })
            new_user_id = result.inserted_primary_key.id

            conn.commit()
            return new_user_id
        
    def get_user(self, username=None, pid=None):
        if username is not None:
            with self.engine.begin() as conn:
                result = conn.execute(sqlalchemy.select(self.user_table).where(self.user_table.c.name == username)).one()
                return User(id=result.id, username=result.name, password=result.password, mail=result.mail_address)
        elif pid is not None:
            with self.engine.begin() as conn:
                result = conn.execute(sqlalchemy.select(self.user_table).where(self.user_table.c.name == username)).one()
                return User(id=result.id, username=result.name, password=result.password, mail=result.mail_address)
        else:
            raise ValueError
 