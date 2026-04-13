import time
import logging
from fuzzywuzzy import fuzz, process

# Configure the logging to a file
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s UTC - %(levelname)s - %(message)s')
logging.Formatter.converter = time.gmtime
logging.info("ChatBot initialized successfully.")

def identify_intent(user_query):
    valid_query_choices = [
        "account balance",
        "transaction history",
        "loan options",
        "interest rates",
        "transfer funds"
    ]
    best_match = process.extractOne(user_query, valid_query_choices)
    if best_match and best_match[1] > 80:  # Adjust the threshold as needed
        return best_match[0]
    return None

def input_user_query():
    user_query = input("Welcome to XYZ bank! How can I assist you today?\n")
    logging.info(f"User query: {user_query}")
    return user_query

def process_query(user_query):
    intent = identify_intent(user_query)
    if intent == "account balance" or intent == "transaction history":
        logging.info("Processing account information query.")
        return "Please check the \"Account Overview\" section in the app for balance and transaction information."
    elif intent == "loan options":
        logging.info("Processing loan options query.")
        return "We offer personal loans, home loans, and auto loans. Please visit our website for more details."
    elif intent == "interest rates":
        logging.info("Processing interest rates query.")
        return "Our current interest rates are 7.5% for personal loans, 6.8% for home loans, and 8.2% for auto loans."
    elif intent == "transfer funds":
        logging.info("Processing fund transfer query.")
        return "To transfer funds, please use the \"Transfer\" feature in our mobile app or online banking portal."
    else:
        logging.warning("Unrecognized user query.")
        return "I'm sorry, I didn't understand your request. Handing over to a human agent."
    
def main():
    while True:
        user_query = input_user_query()
        if user_query.lower() in ["exit", "quit"]:
            logging.info("User requested to exit.")
            print("Thank you for using XYZ bank chatbot. Have a great day!")
            break
        response = process_query(user_query)
        print(response)

if __name__ == "__main__":    
    main()
