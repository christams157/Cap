
import requests
import json
import pickle
from config import API_KEY as api_key


from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    user_message = request.json.get('user_message', '')

    def generate_flask_response(user_message):


        api_endpoint = "https://api.openai.com/v1/chat/completions"

        # Set the conversation history and user prompt
        chat_role = """
        You are a helpful NFL fantasy football assistant who specializes in quarterbacks, running bracks, wide receivers, and tight ends. Users will ask you questions about NFL players. You will provide infomation to fill in the following function: summary_stats(players, different_styles)

        Player's Name (players): A list containing the player's name(s) in the format 'Last name, First name'. Correct any misspellings of the player's name.
        Different Styles should be a list of the same name typed slightly differently. Some players have periods or other punctuations in their name,
        so to make sure you get the right one make a variation of 3. 
        as you can see, each name is still in the format of 'Last name, First name'. Make sure to make 3 for each not including the orginal you made!

        Here is an example:  Burrow, Joe; Burrow, Joe.; Burow, Joe; Burrow, J. 

        Ignore the question they are asking, just focus on the players and answering in the format: players; different styles

        If more than one player is mentioned than do this for each indivual player

        MAKE SURE THE ONLY THING YOU WRITE IS IN THE FORMAT OF "players; different styles" PER PLAYER Nothing Else!!!
        If there is more than one player, make sure to seperate the two formats with "\n"! 
        for example: Stafford, Matthew; Stafford, Matt; Stafford, M.\n
        Burrow, Joe; Burrow, Joe.; Burow, Joe; Burrow, J.
        """



        conversation_history = [
            {"role": "system", "content": chat_role},
            {"role": "user", "content": user_message},
            #{"role": "system", "content": f""}
        ]




        # Prepare the payload
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": conversation_history,
            "max_tokens": 50,
            "temperature" : 0.8
        }

        # Set the headers with the API key
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Send the API request
        response = requests.post(api_endpoint, data=json.dumps(payload), headers=headers)

        # Process the API response
        if response.status_code == 200:
            data = response.json()
            assistant_reply = data['choices'][0]['message']['content']
            print("Assistant:", assistant_reply)
        else:
            print("Error:", response.status_code, response.text)


        with open("Prediction_5.pkl", 'rb') as pickle_file:
            Predictions = pickle.load(pickle_file)
        
        components = assistant_reply.split("\n")
        inputs = []
        for x in components:
            print(x)
            inputs.append(x.split(";"))
        player_stats = []
        for x in inputs:
            Clean_Predictions = []
            for col in x:
                if "Past_Game" not in col:
                    Clean_Predictions.append(col)
            player_stats.append(Predictions[x[0]])
            print(x[0])

        chat_role = """
        You are a magical talking capybara explain how a player in the nfl is. The player stats are in the list total, 
        make sure to always have a stance/opinion, while still sounding nonbias! 
        Don't let the answer depend on the user, make a definitive answer!!! Respond in 100 words or less!!!
        Make sure to talk about and explain some of the stats by showing the numbers
        Don't give them warnings... talk with CONIFDENCE as if it is mostly likely true
        Don't tell them to consider anything, you come up with your own conclusions 
        and logic for why the preiction is what it is based on the data
        Start with something like according to my calculations
        Don't bring up any other variables/factors than the ones we have already
        Projected points arent everything, Some positions skills are more rare than others/harder to replace, but still talk about the projections.
        RB's the hardest to replace while QB are the easiest to replace
        """






        conversation_history = [
            {"role": "system", "content": chat_role},
            {"role": "user", "content": user_message},
            {"role": "system", "content": f"The list with the stats is {player_stats}. The first element is the name, the last element is the list of preidtions, everything inbetween is the whole career stats organised as 'average:STD', also don't say DK, for example, 20 ppr points, not DK points"}
        ]




        # Prepare the payload
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": conversation_history,
            "max_tokens": 250,
            "temperature" : 1
        }

        # Set the headers with the API key
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Send the API request
        response = requests.post(api_endpoint, data=json.dumps(payload), headers=headers)

        # Modify the API response to return HTML content
        if response.status_code == 200:
            data = response.json()
            assistant_reply = data['choices'][0]['message']['content']
            #return f"<div><h2>CappyBalla's Responce:</h2><p>{assistant_reply}</p></div>"
            return f"CappyBalla's Responce: {assistant_reply}"
        else:
            return f"Error: {response.status_code}, {response.text}"


        assistant_response = f"Assistant: {assistant_reply}"

        return assistant_response
    
    assistant_response = generate_flask_response(user_message)

    return jsonify({'flask_response': assistant_response})


if __name__ == '__main__':
    app.run(debug=True)
