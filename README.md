Daily Journal Manager – Command-Line Diary System
A simple command-line diary tool to write, read, and delete journal entries saved by date.
This project allows you to maintain a personal diary directly from the terminal.

Features
Write entries for the current date or a specified date.

Read past entries by selecting a date.

Delete entries when no longer needed.

Entries are stored as plain text files with date-based filenames.

Clean and minimal CLI interface.

Tech Stack
Python 3

File I/O for storing entries.

Datetime for managing date-based entries.

Installation
Clone this repository:

bash
Copy
Edit
git clone https://github.com/yourusername/daily-journal-manager.git
Navigate to the project directory:

bash
Copy
Edit
cd daily-journal-manager
Run the program:

bash
Copy
Edit
python journal.py
Usage
When you run the program, you’ll be presented with a menu:

Write a new entry – Create or update your journal for today or any date.

Read an entry – View your saved journal for a specific date.

Delete an entry – Remove unwanted entries.

Exit – Quit the program.

Example:
bash
Copy
Edit
Welcome to Daily Journal Manager
1. Write Entry
2. Read Entry
3. Delete Entry
4. Exit
Choose an option: 1
Enter date (YYYY-MM-DD) or press Enter for today: 
Start writing your journal entry:
> Had a productive day learning Python!
File Structure
journal.py – Main script.

entries/ – Folder where journal files are stored (automatically created).

Future Enhancements
Password-protected entries.

Search entries by keyword.

Export to PDF or Markdown.

Support for tagging and categorizing entries.

Contributing
Contributions are welcome!
Feel free to open issues or submit pull requests.
