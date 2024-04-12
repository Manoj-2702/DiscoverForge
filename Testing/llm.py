import json
from dotenv import load_dotenv
from os import getenv
import google.generativeai as genai

load_dotenv()
google_token=getenv("GOOGLE_API_KEY")

def list_products_google(msgData):
    genai.configure(api_key = google_token)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(f"""{msgData} \n Imagine a digital assistant meticulously analyzing a diverse collection of announcements related to the launch of new products and services in various industries. This assistant is tasked with identifying and categorizing each product or service mentioned, discerning whether each one represents a fresh market entry or an update to an existing offering. The goal is to compile this information into a straightforward, accessible format. Specifically, the assistant is required to present its findings as a list, focusing solely on the names of these products or services, neatly organized into an array. The array should exclusively contain the names, clearly distinguishing between novel introductions and updates to pre-existing entities, thus providing a clear, concise overview of the recent developments highlighted in the announcements.  Give the output in a json format which gives the product name and the status of the same whether its a new product or just a update to the existing product. The status should either be New Product or Update to existing product.""")

    return response.text

msg=""" 
ANNOUNCEMENT !
@CrossTheAges just released the #GeneralAvailability of the #TCG game and with it we are proud to be launching our official website to help new players and keep you updated! 

https://arkhante.com

Let s go through what you will find there 

No-code editor updates are now generally available for Stream Analytics! Simplify your data analytics and processing tasks without writing any code. Learn more about these updates and try them out today.

#NoCode #DataAnalytics #GeneralAvailability
https://bit.ly/3lpDzs1

Revolutionizing Real-Time Multiplayer Collaboration with AI: Sequoia Capital Backs PartyKit

#AI #artificialintelligence #flexibility #generalavailability #HumanAIcollaboration #llm #machinelearning #Media #opensourcedeploymentplatform #PartyKit

https://multiplatform.ai/revolutionizing-real-time-multiplayer-collaboration-with-ai-sequoia-capital-backs-partykit/ 

Improved Text Analytics In BigQuery: #Search Features Now GA https://cyberpogo.com/2022/11/25/improved-text-analytics-in-bigquery-search-features-now-ga/  #googlecloud #generalavailability #bigquery #indexing #query #dataanalytics

Improved Text Analytics In BigQuery: #Search Features Now GA https://globalcloudplatforms.com/2022/11/25/improved-text-analytics-in-bigquery-search-features-now-ga/  #indexing #query #generalavailability #bigquery #dataanalytics #googlecloud
"""

x=list_products_google(msg)
with open("products.json", 'w') as file:
    json.dump(x, file, indent=4)