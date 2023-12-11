



### Open Questions
#### Usage of Endpoints
In the method call PATCH `/{gameID}/card/{player-id}/{line-id}/{card-name}` there is no actual ressource `card-name` at the given endpoint, instead the URI has parameters that I use to perform the update.
To me this seems like an unclean implementation of the REST API pattern.
However, as I am a beginner with the REST API pattern, I leave this at it is to dig deeper into the topic.




### Endpoints

Create game etc

* `/game`

#### Play a card
* Path: `/{gameID}/card/{player-id}/{line-id}/{cardName}`
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
* Path: `/battle-line/{gameID}/hands/{playerID}`
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

- Getting the current hand: `curl -X GET http://127.0.0.1:5000/0/hands/0`
- Put back some cards onto a stack from a hand: `curl -X PATCH http://127.0.0.1:5000/0/hands/0   -H 'Content-Type: application/json'   -d '{"put_back":["Y1", "Alexander"]}'`
- Draw some tactic cards: `curl -X PATCH http://127.0.0.1:5000/0/hands/0   -H 'Content-Type: application/json'   -d '{"num_tactic_cards":1}'`