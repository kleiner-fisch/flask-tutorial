


### Requirements
The following versions of packages are used:
- Flask==3.0.0
- marshmallow==3.20.1
- parameterized==0.9.0
- SQLAlchemy==2.0.23

### Open Questions
#### Usage of Endpoints
In the method call PATCH `/{gameID}/card/{player-id}/{line-id}/{card-name}` there is no actual ressource `card-name` at the given endpoint, instead the URI has parameters that I use to perform the update.
To me this seems like an unclean implementation of the REST API pattern.
However, as I am a beginner with the REST API pattern, I leave this at it is to dig deeper into the topic.




### Endpoints

Create game etc

* `/game`


#### Get Game State
* Path: `/{game-id}`
* Method: GET
* Body: No body

##### Response
* HTTP Status
** 200 OK if action was succesful
*** Body: 
{
  "claim": {},
  "current_player": 0,
  "game_id": 0,
  "lines": [ LINE ],
  "p0": 0,
  "p1": 1,
  "public_cards": [],
  "unresolved_scout": false
}
with LINE being 
    {
      "sides": {
        "0": ["A4", "ALEXANDER"],
        "1": []
      },
      "won_by": null
    }

** 404 NOT FOUND if user is not authorized

#### Get Hand
* Path: `/{game-id}/hand`
* Method: GET
* Body: 
** ```{
        "username" : "sefie",
        "password" : "abc"
    }```

##### Response
* HTTP Status
** 200 OK if action was succesful
*** Body: `{ "cards" : ["ALEXANDER","C1"]}`

** 404 NOT FOUND if user is not authorized

#### Play a card
* Path: `/{game-id}/card/{player-id}/{line-id}/{card-name}`
* Method: PATCH
* Body: Examples:
** For most cards: ```{}```
** For some tactics (for DESERTER and REDEPLOY the specified card is taken from its current line, and put to the line where DESERTER/REDEPLOY has been played): ```{
        "affected_card": "CARD_NAME",
    }```

##### Response
* HTTP Status
** 200 OK if action was succesful
** 404 NOT FOUND if user is not authorized
** 422 UNPROCCESSABLE ENTITY if user is authorized but data is invalid, or move is illegal. Causes the player to lose.

#### Reject/Accept Claims
**TOBEDONE**

* Path: `/game/{gameID}`
* Method: PATCH
* Body: Examples:
** ```{
        "username" : "sefie",
        "password" : "abc",    
        "action": "ACCEPT_CLAIM"
    }```
** ```{
        "username" : "sefie",
        "password" : "abc",
        "action": "REJECT_CLAIM",
        "counterExample": ["CARD1", "CARD2", "CARD3"]
    }```

##### Response
* HTTP Status
** 200 OK if action was succesful
*** Body: ```
    {
        "lineID": 2, "wonBy": 0
    }```
** 404 NOT FOUND if user is not authorized
** 422 UNPROCCESSABLE ENTITY if user is authorized but data is invalid, or move is illegal. Causes the player to lose.


#### Make Claims
**TOBEDONE**

* Path: `/game/{gameID}/{line-id}`
* Method: PATCH
* Body: Examples:
** ```{
        "username" : "sefie",
        "password" : "abc",    
        "action": "MAKE_CLAIM"
    }```

##### Response
* HTTP Status
** 200 OK if action was succesful
** 404 NOT FOUND if user is not authorized
** 422 UNPROCCESSABLE ENTITY if user is authorized but data is invalid, or move is illegal. Causes the player to lose.

#### Draw/Put back cards
This either happens at the end of the turn, when a single card is drawn, or because SCOUT has been played, when first 3 cards are drawn, and afterwards two cards are put back. This is the only case where cards are put back.
* Path: `/{gameID}/hands`
* Method: PATCH
* Body: Examples
** ```{
        "username" : "sefie",
        "password" : "abc",
        "putBackCards": ["CARD1", "CARD2"],
        "playerID" : 1,
    }```
**  ```{
        "username" : "sefie",
        "password" : "abc",
        "drawTacticsCards": 2,
        "drawNumberCards": 1,
        "playerID" : 1,
    }```

##### Response
* HTTP Status
** 200 OK if action was succesful
*** Body (The resulting hand): ```
    {
        ["CARD1", ...]
    }
    ```
** 404 NOT FOUND if user is not authorized
** 422 UNPROCCESSABLE ENTITY if user is authorized but data is invalid, or move is illegal. Causes the player to lose.

### Manually Playing Around

#### In-Game Commands
- Get the state of the game with id 0 (only the state known to both players): `curl -X GET http://127.0.0.1:5000/game/1`
- Getting the current hand: `curl -X GET http://127.0.0.1:5000/game/3/hand -H 'Content-Type: application/json'   -d '{"username": "sefie3", "password":"abc"}'`
- Put back some cards onto a stack from a hand: `curl -X PATCH http://127.0.0.1:5000/game/3/hand   -H 'Content-Type: application/json'   -d '{"username": "sefie", "password":"abc", "put_back":["A1", "ALEXANDER"]}'`
- Draw some tactic cards: `curl -X PATCH http://127.0.0.1:5000/game/3/hand   -H 'Content-Type: application/json'   -d '{"num_tactic_cards":3, "username": "sefie", "password":"abc"}''`
- Play a number card:  `curl -X PATCH http://127.0.0.1:5000/game/1/0   -H 'Content-Type: application/json'   -d '{"username": "sefie3", "password":"abc", "card":"A5", "action":"PLAY_CARD"}'`
- Play a guile tactic: `curl -X PATCH http://127.0.0.1:5000/game/3/7   -H 'Content-Type: application/json'   -d '{"username": "sefie", "password":"abc", "card":"REDEPLOY", "affected_card":"C5", "action":"PLAY_CARD"}'`
- Claim a line: `curl -X PATCH http://127.0.0.1:5000/game/3/7   -H 'Content-Type: application/json'   -d '{"username": "sefie", "password":"abc", "action":"MAKE_CLAIM"}'`

#### Out of Game Commands
- Create a new user: `curl -X POST http://127.0.0.1:5000/user   -H 'Content-Type: application/json'   -d '{"password":"abc", "username": "sefie", "mail": "mail"}'`
- Create a new game: `curl -X POST http://127.0.0.1:5000/game   -H 'Content-Type: application/json'   -d '{"username": "sefie3", "password":"abc", "username_other":"sefie"}'`



