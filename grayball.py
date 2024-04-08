from flask import Flask,render_template, request, jsonify
import os, sys
from flask_cors import CORS

#sys.path.append("/home/deepak/grayball_final")
from final_output import get_query_answer

grayball = Flask(__name__)
CORS(grayball)
@grayball.route("/chat", methods=['POST'])
def chat_with_ai():
    # Parse the incoming JSON request
    data = request.get_json()
    
    # Extract the message from the request data
    userText = data.get('msg')
    
    
    
    # Ensure there's a message to process
    if not userText:
        return jsonify({"error": "No message provided"}), 400
    
    final_answer, link_list, context = get_query_answer(userText)
    
    if isinstance(final_answer, list):
    	full_text = ""
    	for uu in final_answer:
    		full_text += uu
    		
    else:
    	full_text += final_answer
    # Return the model's response as JSON
    return jsonify({"response": full_text})

if __name__ == "__main__":
    grayball.run()
