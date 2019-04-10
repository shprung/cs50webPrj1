# Project Requirement and implementations

**Registration: Users should be able to register for your website, providing (at minimum) a username and password.**

In the login page, which is the defualt page, you can find a link: "Not a member? Register as a new member." that will take you to the registration.
On top of the login and password I also ask for your gender/sex and your age group. Upon submit I do some validation and will return error is I found any.
If no error found, you will be redirected to the login page with a message that your account was created successfully.


**Login: Users, once registered, should be able to log in to your website with their username and password.**

The login page, whis is the default page, will validate your login/pass and will report if you fail to login. Upon login you will no longer will need to login until you logout. 

**Logout: Logged in users should be able to log out of the site.**

Implemented.

**Import: Provided for you in this project is a file called books.csv, which is a spreadsheet in CSV format of 5000 different books. Each one has an ISBN number, a title, an author, and a publication year. In a Python file called import.py separate from your web application, write a program that will take the books and import them into your PostgreSQL database. You will first need to decide what table(s) to create, what columns those tables should have, and how they should relate to one another. Run this program by running python3 import.py to import the books into your database, and submit this program with the rest of your project code.**

Implemented.

**Search: Once a user has logged in, they should be taken to a page where they can search for a book. Users should be able to type in the ISBN number of a book, the title of a book, or the author of a book. After performing the search, your website should display a list of possible matching results, or some sort of message if there were no matches. If the user typed in only part of a title, ISBN, or author name, your search page should find matches for those as well!**

I noticed the the native search was case sensitive so I impelemnt a not case sensitive search to help the visitor to find her/his book.

**Book Page: When users click on a book from the results of the search page, they should be taken to a book page, with details about the book: its title, author, publication year, ISBN number, and any reviews that users have left for the book on your website.**

The book page implement all the requirement and also include a photo of the book cover using googleapi.com/book call.

**Review Submission: On the book page, users should be able to submit a review: consisting of a rating on a scale of 1 to 5, as well as a text component to the review where the user can write their opinion about a book. Users should not be able to submit multiple reviews for the same book.**

I am listing the review in order of newest first. I also offer a delete-my-review in order to allow you to remove your review and maybe add a new one. this have two benefits: (1) you can use it to edit your review. (2) it allow you to push your review to the top because it will be the newest.
I also do basic validation in order ro eliminate empty or very short (few charcters only) reviews.

**Goodreads Review Data: On your book page, you should also display (if available) the average rating and number of ratings the work has received from Goodreads.**

Implemented. I also implemented a API call to googleapi/book to gother some more interesting info like how many pages in the book and of course the image of the book cover.

**API Access: If users make a GET request to your website’s /api/<isbn> route, where <isbn> is an ISBN number, your website should return a JSON response containing the book’s title, author, publication date, ISBN number, review count, and average score.**

Implemented.


------------------------------------------------

#setting the env
set FLASK_APP=application.py
set FLASK_DEBUG=1
set DATABASE_URL=postgres://ebxdqqfagubuiq:f56752a1e3f19e90e43f5c3e819da1a8ac1aad001d41291dc9db847a94bb88ee@ec2-50-17-231-192.compute-1.amazonaws.com:5432/de8ncfmvn4hh78

#running the app
flask run

