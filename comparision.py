import mysql.connector as mycon
import http.client
import requests
import urllib3
from time import sleep
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, redirect , url_for
import socket


hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

print("Hostname:", hostname)
print("IP Address:", ip_address)

app = Flask(__name__)
users = {
    "user1": "password1",
    "user2": "password2",
    "user3": "password3"
}

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # extract the username and password from the form data
        username = request.form["username"]
        password = request.form["password"]
        
        # check if the username and password are valid
        if username in users and users[username] == password:
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid username or password.")
    else:
        return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # extract the username and password from the form data
        username = request.form["username"]
        password = request.form["password"]
        
        # check if the username is already taken
        if username in users:
            return render_template("signup.html", error="Username already taken.")
        else:
            # add the new user to the dictionary of valid usernames and passwords
            users[username] = password
            return redirect(url_for("login"))
    else:
        return render_template("signup.html")

# Establish database connection
#connection = mycon.connect(
#   host="LAPTOP-NG9VKEUU",
#    user="Priya",
#   password="Priya@123",

#)
#print(connection,"connection establised")
#http=httplib2.Http()

def get_flipkart_price(product):
    try:
        url = f"https://www.flipkart.com/search?q={product}"
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.content, "html.parser")
        product_link = soup.find("a", attrs={"class": "_1fQZEK"})
        if not product_link:
            return None
        product_url=""
        product_url = "https://www.flipkart.com" + product_link["href"]
        response = requests.get(product_url, timeout=30)
        soup = BeautifulSoup(response.content, "html.parser")
        price = soup.find("div", attrs={"class": "_30jeq3"})
        if not price:
            return None
        price_text = price.text.replace(",", "").replace("₹", "")
        return float(price_text)
    except requests.exceptions.RequestException as e:
        print("Connection error:",e)
        return None

def get_amazon_price(product):
    try:
        url = f"https://www.amazon.in/s?k={product}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.content, "html.parser")
        product_link = soup.find("a", attrs={"class": "a-link-normal"})
        if not product_link:
            return None
        product_url=""
        product_url = "https://www.amazon.in" + product_link["href"]
        response = requests.get(product_url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.content, "html.parser")
        price = soup.find("span", attrs={"class": "a-price-whole"})
        if not price:
            return None
        price_text = price.text.replace(",", "")
        return float(price_text)
    except requests.exceptions.RequestException as e:
        print("Connection error:",e)
        return None
        
#def save_product_to_database(product, flipkart_price, amazon_price):
#    cursor = connection.cursor()
#    query = "INSERT INTO products (name, flipkart_price, amazon_price) VALUES (%s, %s, %s)"
#    values = (product, flipkart_price, amazon_price)
#    cursor.execute(query, values)
#    connection.commit()
#    cursor.close()
#    connection.close()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "product" in request.form:
            product = request.form["product"]
            flipkart_price = get_flipkart_price(product)
            amazon_price = get_amazon_price(product)
            if flipkart_price is not None and amazon_price is not None:
                if flipkart_price < amazon_price:
                    result = "Flipkart has the lowest price!"
                    cheapest = "Flipkart"
                elif amazon_price < flipkart_price:
                    result = "Amazon has the lowest price!"
                    cheapest = "Amazon"
                else:
                    result = "The prices are the same on both websites."
                    cheapest = "Both websites"
            else:
                result = "Could not fetch the prices. Please try again later."
                cheapest = ""
            return render_template("index.html", result=result, cheapest=cheapest)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)