# My Basketball Player's All-Time Wish List 

Basketball is a 5*5 team-spirit worldwide known sport. All players have different individual attributes relative to the position they play, whether this could be the height 
(i.e. being a guard vs center) or skills (ex. scoring lots of points, making lots of rebounds etc). As generations pass, players across all continents change but some remain memorable for you even if
they do not play currently. In addition, one would in some place (ex. whether on street or to a coffee place) be able to meet/see them, spend time and both sides could share knowledge, ideas 
and emotions. The site provides you to insert these players, the top three disciplines on each player you admire and how much virtually one would spend relative to the place you choose
(brunch, coffee, street) to see your top five favorite athletes.        

## UX

- The strategy plane: Aim to achieve a website about Basketball sport.
  Target audience :
  - People surrounded by the sport business and those who enjoy playing and/or watching the sport.

- The scope plane: 
  - Features :
    - A login/logout Form
    - Add Player - Edit / Delete Player Form
    - List Summary Charts and Table Information of your players

- The structure plane: 
  - Info is structured in a standard way. First page are input fields and button to Login to your account
  - A List Summary and Add Player button
  - Two aspects (piechart, barcharts and table). Grouped displayed first (birth region and virtual spend charts), displayed second (table players whole summary) accompanied by an
    edit/delete individual player button

- The skeleton plane: 
  - Page info represented from left to right (or top to bottom) concept :
    - Minimal header text written with lots of indicative icons 
    - Three buttons (show players, add a player, edit/deleting a player)
    - Two d3.js graphs (pie chart, horizontal bar chart)
    - One Horizontal and vertical scrollable table

- The surface plane: 
  - Colours : a darker navbar but a contrast white opaque and brighter colours to the body section for one to view the graphs per horizontal and vertical axis more clearly.
  - Semantic : header, nav, section, form, materialize (row, column grid, color, buttons), i tags
  - Typography : google fonts and materialize libraries like table highlight class to demonstrate description. Material icons to highlight the input field meaning.
  - Jinja helper to loop through html objects and also to pass info to JS. JS and JQuery for materialize js, show players existence and actions when document is loaded, 
    graph creation and table scrolling. 

##### User Stories list:

- As a developer :
  - I insert a summary table of existing players so that I can achieve
    - scrolling for responsive design
    - edit button at the end of each row per player, easy to adjust values to obtain user flexibility
  - Main two chart types (barchart and piechart) and attributes chosen are distinct (birth region and virtual spend) to achieve diversity  
  - Modal insert on edit and delete player to achieve a cross-check decision.

- As a user : 
  - Having several players registered, I would like to be displayed on a chart above my table, the top five players willing to spend more to meet in person.
  - On Player forms, since there are several fields, I like the idea of having less fields to insert and more fields to choose.
  - As the rating is ranged from 1 to 10 on disciplines and 1 to 20 on virtual times, I like the idea of beeing able to insert a decimal and distinct
    any close preference among disciplines, virtuals and players.

A mockup frame of the website, one could find it at the attached pdf file at the directory mockup_frame. db-schema on page 2 inside the pdf file.

## Features


### Existing Features

- Above mentioned on the structure and skeleton plane

---

Currently, the website provides with a general but on point overview of the subject. Additional plans to be implemented in the future would be :

- Make deleting a player more flexible rather than having to go to the edit player to achieve it.
- Login Form add minimum characters and an EmailJS forgot password.
- More python data scientific
  - Insert a text area field and one guest can comment per individual player if interested. Extract most common words with various players and plot categorical charts. 
  - Make virtual spend calculation more python data scientific and use category birth region, discipline and virtual spend fo anything regressed or classified.

### Features Left to Implement

- Reorder the Table Summary for name to be at the first column and in absolute positioning. Therefore when one scrolls horizontally has a clearer picture of
  the player. Currently the row is highlighted and is a helper.
- Add a category list for people to be able to add more favorite disciplines from the already existing ones.
- Fit a number percentage discrete label text on pie chart and two decimal points on rating and virtual timing (currently fits one decimal). 

## Technologies Used

- [Flask Python](http://flask.pocoo.org/)
    - The project uses **Flask Python and Jinja** for web development.

- [HTML5]
    - The project uses **HTML5** to structure the webpages.

- [CSS3](https://github.com/feddieminas/project_om/blob/master/assets/css/style.css)
    - The project uses **CSS3** to style the webpages.

- [Materialize CSS JS](http://archives.materializecss.com/0.100.2/)
    - The project uses **Materialize CSS JS 0.100.2** to create navigation bar, forms, styles, text and display classes.
    
- [Material Icons](https://material.io/tools/icons/?style=baseline)
    - The project uses **Material Icons** to insert icons for a user friendly visualisation and navigation. 

- [MongoDB](https://mlab.com/)
    - The project uses **MongoDB** to archive guest account players data.

- [JQuery](https://jquery.com)
    - The project uses **JQuery** to enable interactivity of slider and dropdown buttons.

- [D3 JS](https://cdnjs.com/libraries/d3)
    - The project uses **D3 JS** for data type, formats, selecting elements and functions. 

- [Chrome DevTools](https://developers.google.com/web/tools/chrome-devtools/)
    - The project uses **Chrome DevTools** to simplify editing pages on-the-fly and assist you to responsive design. 


## Testing

- Used Python unittest module framework to test :
  -     

----

Encountered issues:


 

## Deployment

I deployed the project on [Heroku](https://dashboard.heroku.com/apps/basketball-players-favs).

Worked on Google Chrome and Safari Version.

One could run locally by executing the app.py file and retrieve the URL to login. 

## Credits


### Content

- The minimal text content is self-inspired.

### Media

- The photo in this section was obtained from [theartmad](https://theartmad.com/).

### Acknowledgements

- I received inspiration for this project from networking apps (i.e. make a wish) and myself having a passion for sports and basketball.