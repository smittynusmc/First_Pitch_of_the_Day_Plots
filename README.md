MLB First Pitch Visualization Tool
This Python application fetches and visualizes the first pitch of MLB games for a specified date using the SportsRadar MLB API. It displays the pitch location within the strike zone along with game details in a GUI format.

Prerequisites
Before you run this application, ensure you have the following installed:

Python 3.6 or higher
matplotlib
requests
tkinter (usually included with Python)
Installation
Clone the repository:
bash
Copy code
git clone https://your-repository-url-here.git
cd your-repository-directory
Install required Python packages:
bash
Copy code
pip install matplotlib requests
Configuration
You need a valid API key from SportsRadar to fetch the MLB data. Follow these steps to configure your API key:

Obtain an API Key:
Visit SportsRadar and sign up for an API key for the MLB API.
Configure your API Key in the Script:
Open the todays_first_pitch.py file in a text editor.
Find the line that defines the api_key variable. Replace 'your_api_key_here' with your actual API key from SportsRadar.
python
Copy code
api_key = 'your_api_key_here'  # Replace 'your_api_key_here' with your actual SportsRadar API key
Save the changes.
Usage
Run the script using Python. Make sure you are in the project directory:

bash
Copy code
python todays_first_pitch.py
Upon running the script, a graphical user interface will open. You will need to enter the date for which you want to view game data in the format YYYY, MM, DD. After entering the date and clicking the "Load Game Data" button, the application will fetch data for the given date and display the first pitch of each game in a new tab within the application window.

Features
Data Fetching: Retrieves game and pitch data from the SportsRadar MLB API.
Visualization: Displays the location of the first pitch within the strike zone for each game on the specified date.
Interactive GUI: Allows users to specify the date and retrieve the data via a user-friendly interface.
Troubleshooting
Ensure your API key is valid and has not exceeded the usage limits.
Check your internet connection if the application fails to fetch the data.
If matplotlib does not show the plots, ensure it's installed correctly and compatible with your version of Python.
Contributing
Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.

License
This project is licensed under the MIT License - see the LICENSE file for details.






