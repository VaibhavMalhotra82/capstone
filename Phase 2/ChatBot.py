import time
import logging

# Configure the logging to a file
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s UTC - %(levelname)s - %(message)s')
logging.Formatter.converter = time.gmtime
logging.info("ChatBot initialized successfully.")

def input_user_query():
    user_query = input("Welcome to XYZ bank! How can I assist you today?\n")
    logging.info(f"User query: {user_query}")
    return user_query

def process_query(user_query):
    if "account balance" in user_query.lower():
        logging.info("Processing account balance query.")
        return "I'm sorry, I cannot provide real-time account balance information."
    elif "transaction history" in user_query.lower():
        logging.info("Processing transaction history query.")
        return "I'm sorry, I cannot provide real-time transaction history information."
    elif "loan options" in user_query.lower():
        logging.info("Processing loan options query.")
        return "We offer personal loans, home loans, and auto loans. Please visit our website for more details."
    elif "interest rates" in user_query.lower():
        logging.info("Processing interest rates query.")
        return "Our current interest rates are 7.5% for personal loans, 6.8% for home loans, and 8.2% for auto loans."
    elif "transfer funds" in user_query.lower():
        logging.info("Processing fund transfer query.")
        return "To transfer funds, please use the \"Transfer\" feature in our mobile app or online banking portal."
    else:
        logging.warning("Unrecognized user query.")
        return "I'm sorry, I didn't understand your request. Please try again."
    
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
