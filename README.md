# Books For Kooks
#### Description:

Books For Kooks is a web application created using Flask,SQL,HTML,CSS and Python where a user can register an account and then find information about a book they wish to read and also find reviews about a book from other people who have already read the book. The web application also allows you to create a personalized bookshelf where you add books that you want to buy and read, are planning to read or one's that you have already read. Users are required to sign in and create an account before using the web application ensuring safety and privacy. The app uses SQL to store user accounts, books, and reviews, ensuring data is saved and organized. It allows readers to organize their reading, discover new books, and learn from community reviews, making the reading experience more enjoyable and social.

#### TEMPLATES:
layout.html: This template has the basic layout of my website. It contains the title at the top as well as a navbar for user's to navigate throughout the website.
addshelf.html: This template contains a form where user's can enter information about the book they wish to add to their bookshelf.
bookshelf.html: This template contains a table that populates all of the books in your bookshelf into a table.

bookinfo.html: This template contains a form where users can enter information about a book they wish to find a description about.
bookinforesults.html: This template contains a table that shows the description of the book the user asked for.

index.html: This template contains the homepage of the website with a welcome to Books For Kooks image
reviews.html: This template contains a form where users can enter information about a book they wish to find reviews on
reviewsresults.html: This template shows a table to the user of each of people who wrote the review's name as well as what score they gave the book out of 5 and a description as to what they thought of the book. The reviews shows a maximum of 10 reviews.

login.html: This template contains a form where a user can enter their existing username and password in order to log into their account and restore anything they had going on in Books for Kooks previously.
signup.html: This template contains a form where a user can sign up for an account by entering a username that doesn't already exist and a password.

#### STATIC:
The static folder contains two images, one for the logo of the website and another for the welcome page of the website.

#### DATABASE:
books.db contains four tables. bookdetails and bookratings are tables from the Amazon Reviews csv files, book_data.csv and Books_rating.csv, which contains information about books such as customer reviews, summaries, authors, etc. users is a table that contains the if for each user as well as their username and password. the bookshelf database contains each user's bookshelf with the title and author of each book as well as the status of whether the user read the book or wants to read the book.

#### APP.PY:
This is the main file which uses flask to connect SQL, Python, CSS and HTML together. It contains 7 different routes.

"/": This route takes you to the homepage where it welcomes you to Books For Kooks. When you are on the homepage, you can still see the navbar to take you to other parts of the website.

"/login": This route takes you the login page, where you fill out the form with your username and password. If your username is in the SQL database and matches your password, then you will directly be rerouted to "/" which is the homepage.

"/logout": This route logs you out of your account and takes you back to the "/" route filled with the homepage.

"/signup": This route takes you to the signup page, where you can sign up by providing a username and a password. If you don't fill out one of the parameters and click sign up, it will tell you to resubmit the form. After signing up, it will redirect you to the login page where you can now log in.

"/bookinfo": This route takes you to the book info page. Since the user needs to be logged in in order to use this page, it checks if the user_id is in the session and if it isn't, it redirects them to the log in page. Or else, they can use this page to find info about any book. Once they search up a book, it will redirect them to the bookinforesults.html.

"/reviews": This route takes you to the book reviews page. Since the user needs to be logged in in order to use this page, it checks if the user_id is in the session and if it isn't, it redirects them to the log in page. Once the user searches up a review for a book, it will redirect them to the results page.

"/addshelf": This route takes you to add shelf page where user's can enter information about a book to add it to their shelf.

"/bookshelf": Thie route takes you to the user's bookshelf where user's can see all the books they added from the addshelf route. Again, if the user is not logged in and tries to use this route, it will redirect them to the login page.

#### DESIGN CHOICES:
While creating the application Books For Kooks, I did face some design choices where I had trouble picking which path to take. For example, I didn't know whether I wanted to have user's to be able to add to the bookshelf on the same page as the bookshelf. Some pros to this would be that they would be able to see what book's they already have in their shelf to ensure that they don't double add the same one. However, some cons to this were that there would be too much on one page which can become overstimulating for the user. In the end, I decided to make them on seperate pages.


#### ABOUT ME:
Hi my name is Medha and I am currently 18 years old. I am the owner of Books For Kooks. One of my strongest passions is coding and I have been coding for the past few years. I hope to find a career as a software engineer!
# Books-For-Kooks
