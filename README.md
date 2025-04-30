University Recommender System Hi! I'm building an intelligent University Recommender System that helps students around the world find the most suitable universities based on their academic background, budget, and preferences. This project is especially designed for students who are looking for funded or affordable study opportunities abroad.

🔍 What I Did I created a full-stack web application using Flask and Python, powered by a custom-made dataset of over 1,000 universities from different countries.

🧠 Features Smart filtering of universities based on: GPA IELTS, SAT, AP scores Budget Major (e.g., IT, Engineering, Medicine, etc.) Preferred climate Project experience level A user-friendly web interface to input criteria and display matching universities. Random sampling from filtered results for diverse suggestions. Extended dataset with additional university metadata: Country, city, cost of living Scholarships and grants Teaching language QS rankings (national and global) Program descriptions

⚙️ Technologies Used Python for backend logic Flask as the web framework Pandas for data processing and filtering HTML + Jinja2 templates for the frontend A large CSV dataset containing university data from all over the world

📁 Files Included app.py — Flask web server model.py — filtering logic based on user input universities_extended_final_large_ru.csv — the main dataset templates/index.html — frontend form and results table

🚀 How to Run Clone the repository Install dependencies: pip install flask pandas Run the app: python app.py Go to http://127.0.0.1:5000 in your browser
