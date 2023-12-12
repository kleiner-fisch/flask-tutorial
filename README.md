


### Requirements
The following versions of packages are used:
- Flask==3.0.0
- marshmallow==3.20.1
- parameterized==0.9.0

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


#### Make and Reject/Accept Claims
**TOBEDONE**

* Path: `/{gameID}/{player-id}/{line-id}`
* Method: PATCH
* Body: Examples:
** ```{
        "action": "CLAIM
    }```
** ```{
        "action": "REJECT_CLAIM,
        "counterExample": ["CARD1", "CARD2", "CARD3"]
    }```

##### Response
* HTTP Status
** 200 OK if action was succesful
*** Body: ```
    {
        "lineID": 2, "wonBy": 0
    }```
*** If there is a stronger line possible than the provided counter example. Body: ```
    {
        "lineID": 2,
        "wonBy": 1,
        "counterCounterExample": ["B10", "B9", "B8"]
    }```
*** If the counter example is invalid because at least one card is not available anymore. Body: ```
    {
        "lineID": 2,
        "wonBy": 1,
        "unavailableCards": ["B10", "B9"]
    }```
** 404 NOT FOUND if user is not authorized
** 422 UNPROCCESSABLE ENTITY if user is authorized but data is invalid, or move is illegal. Causes the player to lose.

#### Draw/Put back cards
This either happens at the end of the turn, when a single card is drawn, or because SCOUT has been played, when first 3 cards are drawn, and afterwards two cards are put back. This is the only case where cards are put back.
* Path: `/{gameID}/hands/{playerID}`
* Method: PATCH
* Body: Examples
** ```{
        "putBackCards": ["CARD1", "CARD2"],
        "playerID" : 1,
    }```
**  ```{
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

- Get the state of the game with id 0 (only the state known to both players): `curl -X GET http://127.0.0.1:5000/0`
- Getting the current hand: `curl -X GET http://127.0.0.1:5000/0/hands/0`
- Put back some cards onto a stack from a hand: `curl -X PATCH http://127.0.0.1:5000/0/hands/0   -H 'Content-Type: application/json'   -d '{"put_back":["Y1", "Alexander"]}'`
- Draw some tactic cards: `curl -X PATCH http://127.0.0.1:5000/0/hands/0   -H 'Content-Type: application/json'   -d '{"num_tactic_cards":1}'`
- Play a number card: `curl -X PATCH http://127.0.0.1:5000/0/card/0/0/F7   -H 'Content-Type: application/json'   -d '{}'`
- Play a guile tactic: `curl -X PATCH http://127.0.0.1:5000/0/card/0/1/DESERTER   -H 'Content-Type: application/json'   -d '{"affected_card":"SHIELD_BEARER"}'`
