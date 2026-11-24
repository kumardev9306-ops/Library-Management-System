LIBRARY MANAGEMENT SYSTEM - UPDATE

Files in this package:
1. database.py   - MySQL connection function
2. dashboard.py  - Updated dashboard with 6 live statistics and Reports navigation
3. reports.py    - Inventory, Issue History, Low Stock reports and CSV export

HOW TO APPLY:
1. Make a backup copy of your current project folder.
2. Replace database.py with the database.py in this package.
3. IMPORTANT: In database.py, replace YOUR_NEW_MYSQL_PASSWORD with your NEW MySQL password.
4. Replace dashboard.py with the dashboard.py in this package.
5. Add reports.py to the same folder as main.py.
6. Do not replace main.py, books.py, students.py or issue_return.py.
7. Run: python main.py

LOW STOCK RULE:
A book title is counted as low stock when its available quantity is 2 or less.
This threshold is used in both Dashboard and Low Stock Books report.

CSV:
Use Export CSV in Reports. The exported file can be opened in Excel.
