## Generated Story 5575656197305734
* greet
    - utter_greet
* restaurant_search
    - utter_ask_location
* restaurant_search
    - utter_ask_cuisine
* restaurant_search{"cuisine": "chinese"}
    - slot{"cuisine": "chinese"}
    - action_restaurant
    - slot{"location": null}
* affirm
    - utter_goodbye
    - export

## Generated Story -7126780661050212038
* greet
* restaurant_search
    - utter_ask_location
* restaurant_search{"location": "delhi"}
    - slot{"location": "delhi"}
* restaurant_search{"cuisine": "chinese"}
    - slot{"cuisine": "chinese"}
    - action_restaurant
    - export

## Generated Story -5937347253993745854
* greet
    - utter_greet
* restaurant_search{"location": "north"}
    - slot{"location": "north"}
    - utter_ask_cuisine
* restaurant_search{"cuisine": "chinese"}
    - slot{"cuisine": "chinese"}
    - action_restaurant
    - slot{"location": "north"}
* goodbye
    - utter_goodbye
    - export

