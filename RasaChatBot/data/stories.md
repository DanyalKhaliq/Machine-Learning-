## policy happy path
* greet
    - utter_greet
    - common_form
    - form{"name": "common_form"}
    - form{"name": null}
    - utter_greetname
* policy_buy
    - utter_Mosquitolink
    - utter_Waterlink
    - utter_Hyperlink
    - utter_ask_digital
* digital_policy
    - action_check_digital
    - utter_ask_confirmpolicy
* affirm
    - utter_ask_disease
* deny
    - utter_ask_hospital
* deny
    - utter_ask_formfill
* affirm
    - policy_form
    - form{"name": "policy_form"}
    - form{"name": null}
    - utter_goodbye
