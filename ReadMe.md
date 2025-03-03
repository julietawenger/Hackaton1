# The BibliOracle
https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/Pinhas/Downloads/DALL%C2%B7E%202025-03-03%2003.43.14%20-%20A%20sleek%20and%20modern%20app%20icon%20for%20%27BibliOracle%27.%20The%20design%20should%20feature%20an%20open%20book%20with%20glowing%2C%20mystical%20pages%2C%20symbolizing%20knowledge%20and%20wisdom.%20.webp?version%3D1740966226384

## Overview
BibliOracle is a **book recommendation system** that helps users find their next great read based on their preferences and reading history. This system includes:
- A **Books Dataset**, cleaned and structured for effective recommendations.
- A **Users Dataset**, which simulates user interactions and preferences.
- A **Custom Book Recommendation Engine** that suggests books based on user behavior and genre similarities.
- An **Interactive Python Script** where users can create an account, rate books, and receive personalized recommendations.
- A **User Analytics Notebook** with visualizations and insights about user reading patterns (example).

## Features
- **Personalized Recommendations**: Get book suggestions based on your reading history and preferences.
- **Surprise Me Option**: Discover randomly suggested books.
- **User Analytics**: Gain insights into user behaviors.
- **Custom Dataset Handling**: Load, clean, and analyze book data efficiently.

## Getting Started
To run this project, follow these steps:

### 1. Clone or Download the Repository
You can either clone the repository or download it manually.

#### Clone via Git (Recommended)
```sh
$ git clone https://github.com/julietawenger/Hackaton1.git
$ cd Hackaton1
```

#### Manual Download
1. Click the green **"Code"** button on GitHub.
2. Select **"Download ZIP"**.
3. Extract the ZIP file to a folder on your computer.

### 2. Install Dependencies
Ensure you have Python installed (>=3.7). Then install required libraries:
```sh
$ pip install pandas numpy faker scipy
```

### 3. Run the Program
Navigate to the project folder and execute:
```sh
$ python interactive_code.py
```

### 4. Interact with the System
- **Create an Account**: Enter your name, age, and preferred genres.
- **Rate Books**: Provide ratings for books you've read.
- **Get Recommendations**: Receive book suggestions based on user data that matches you or get recommendations based on your prefered genres.
- **Explore Analytics**: Open `UsersAnalysis.ipynb` to get a glimps on how an app like this could provide you with insite an detailed information.

## File Structure
```
📂 Hackaton1
 ├── 📜 interactive_code.py        # Main interactive script
 ├── 📜 recommendations_engine.py  # Core recommendation logic
 ├── 📜 simulate_users.py          # Generates sample user data
 ├── 📜 users.csv                  # Simulated user dataset
 ├── 📜 Amazon_books_cleaned.csv   # Cleaned book dataset
 ├── 📜 UsersAnalysis.ipynb        # Jupyter Notebook for analytics
 ├── 📜 ReadMe.txt                 # Project Documentation
```

## Future Enhancements (V2 and beyond)
- browse your personal read and rated book list
- Achivements for gamification and goal setting  
- Implementing **collaborative filtering** for better recommendations.
- Enhancing the **user interface** with a web or mobile app.
- Expanding **analytics** for publishers and authors.

---

Enjoy using **BibliOracle** and never struggle to find your next book again!

