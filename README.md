<p align="center">
  <img src="https://github.com/user-attachments/assets/f254e781-5f23-4c40-ae1d-f60941c24613" width="20%" alt="image0" />
  <img src="https://github.com/user-attachments/assets/124b5828-7d80-4bf3-8bf1-0402a988daa0" width="20%" alt="image1" />
  <img src="https://github.com/user-attachments/assets/e292eb5e-0582-418b-af10-fbc1aefcfc4d" width="20%" alt="image2" />
</p>






# VERSION OVERVIEW
## VERSION 1:
In this version, we created the basic part of the project. We made an Airport class that stores the airport code, its location (latitude and longitude), and whether it is in the Schengen area. We also added functions to work with this data: we can load airports from a file, add new airports, remove airports, and check if an airport is in Schengen using its code.
We also added functions to save only the Schengen airports into a file and to show the information of each airport clearly on the screen. To make the program easier to understand, we created a plot that shows the number of Schengen and non-Schengen airports. We also added a map in Google Earth to show where the airports are, using different colors for each type.
Finally, we built a simple interface using Tkinter so users can use all the features easily. With this interface, users can load data, manage airports, see the plots, and open the map in a clear and easy way.

Link video: https://youtu.be/5_FNSD5ZjNM

## VERSION 2:
In this version, we added the management of flights arriving to Barcelona (LEBL). We created an Aircraft class that stores the aircraft ID, the airline, the origin airport, and the arrival time.
We added functions to work with this data: we can load flights from a file, save them into a file, and ignore lines with incorrect data. We also created different plots such as the number of flights per hour, the number of flights per airline, and a comparison between flights coming from Schengen and non-Schengen countries.
We also added a map in Google Earth to show the routes of the flights from their origin to Barcelona, using different colors depending on whether they come from Schengen countries or not.
In addition, we implemented a function to detect long-distance flights (more than 2000 km), which may need special attention.
Finally, we updated the interface so users can use all these new features easily, including loading flight data, saving it, viewing plots, and displaying routes on the map. 

Link video: https://www.youtube.com/watch?v=_cnyBX8HjV8

## VERSION 3:
In this version, we added the management of the boarding gates at Barcelona airport (LEBL). To do this, we created the BarcelonaAP, Terminal, BoardingArea, and Gate classes, which allow us to represent the structure of the airport. Now, the program loads this structure directly from a text file and reads which terminal is assigned to each airline. With this information, the system automatically searches for a free gate for each arriving flight, checking if the airplane must go to the Schengen or non-Schengen area based on its origin.
Additionally, we used this delivery to fix several mistakes from the previous versions. First, we fully documented the program code by adding explanatory comments using the hashtag symbol. We also added the filter applied to the plots so they show the data correctly, and we repaired the operation of the function that detects long-distance flights.
Finally, we expanded the interface so the user can build the structure of Barcelona airport, assign gates to arriving flights, and see which ones are occupied at any time. As a pending task for the future, we left the integration of the Google Earth window inside the program interface itself, since for now it still opens separately.

Link video:

## VERSION 4:
To be released soon.
