# SheetBrowser

Contains two python scripts: mathpage.py generates a json file documenting all the links to the worksheets, and mathapp.py launches a GUI for selecting the links.

## structure of sheet_links.json
first level is 
`sheet_links = {term_name : term_courses}`

second level is
`term_courses = {course_name : course_sheets}`

third level is 
`course_sheets = {sheet_number : sheet_files}`

fourth level is 
`sheet_files = {file_name : link}`

For example, to access the Sheet3 pudding solutions to Prelims Michaelmas course M1: Linear Algebra, do: <br>
`sheet_links['Prelims - Michaelmas']['M1: Linear Algebra I']['3']['Sheet3_pudding_solutions.pdf']`
