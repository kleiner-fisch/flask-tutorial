from db_setup import * 
import sqlalchemy
import pdb
from game import Game 
from line import Line



def get_game(game_id):
    game_stmt = sqlalchemy.select(game_table).where(game_table.c.id == game_id)
    hand_cards_stmt = sqlalchemy.select(hand_card_table).where(hand_card_table.c.game_id == game_id)
    lines_stmt = sqlalchemy.select(line_table).where(line_table.c.game_id == game_id)
    line_cards_stmt = lambda line_id: \
        sqlalchemy.select(line_card_table).where(line_card_table.c.line_id == line_id)
    with engine.begin() as conn:
        game_result = conn.execute(game_stmt).one()
        hand_p1, hand_p2 = parse_hands(conn.execute(hand_cards_stmt), 
                                      game_result.p1_pid, game_result.p2_pid)
        lines_result = conn.execute(lines_stmt)
        lines = [parse_line(conn.execute(line_cards_stmt(row.id ), 
                                         game_result.p1_pid, game_result.p2_pid))
                                         for row in lines_result]
        game = Game(game_result.p1_pid, game_result.p2_pid, game_result.id,
                   p0_hand=hand_p1, p1_hand=hand_p2,
                    lines=lines)
    return game


        

def parse_hands(db_result, p1_pid, p2_pid):
    cards = [(row.card, row.pid) for row in db_result]
    p1_hands = [c for (c, pid) in cards if pid == p1_pid]
    p2_hands = [c for (c, pid) in cards if pid == p2_pid]
    return (p1_hands, p2_hands)

def parse_line(db_result, p1_pid, p2_pid):
    result = Line(p1_pid, p2_pid)
    result.sides[p1_pid] += [row.card for row in db_result if row.pid == p1_pid]
    result.sides[p2_pid] += [row.card for row in db_result if row.pid == p2_pid]
    return result


def create_game(player_id1, player_id2, starting_player):
    game = Game(player_id1, player_id2, starting_player)
    new_game_id = None                                   
    with engine.begin() as conn:
        result = conn.execute(sqlalchemy.insert(game_table),
        {
            "p1_pid" : game.p0, "p2_pid" : game.p1, "p1_is_current_player" : game.current_player==game.p0,
            "p1_has_claim" :False, "p2_has_claim" : False,
            "unresolved_scout" : False, "game_finished" : False, 
        })
        #pdb.set_trace()
        new_game_id = result.inserted_primary_key.id
        cards_p1 = [{"game_id" : new_game_id, "pid" : game.p0, "card" : c} for c in game.hands[game.p0]]
        cards_p2 = [{"game_id" : new_game_id, "pid" : game.p1, "card" : c} for c in game.hands[game.p1]]

        conn.execute(sqlalchemy.insert(hand_card_table), cards_p1)
        conn.execute(sqlalchemy.insert(hand_card_table), cards_p2)

        conn.commit()
    return new_game_id
    


# insert_stmt = insert(address_table).returning(
#     address_table.c.id, address_table.c.email_address
# )
# print(insert_stmt)
        





# stmt = insert(user_table).values(name="spongebob", fullname="Spongebob Squarepants")


#     conn.execute(
#         text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
#         [{"x": 6, "y": 8}, {"x": 9, "y": 10}],
#     )



# print(
#     sqlalchemy.select(Address.email_address).where(
#         and_(
#             or_(User.name == "squidward", User.name == "sandy"),
#             Address.user_id == User.id,
#         )
#     )
# )
# >>> stmt = select(user_table).where(user_table.c.name == "spongebob")