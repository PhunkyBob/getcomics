# GetComics-Links

Get direct links for [GetComics.info](https://getcomics.info) releases. 

You can search with the following criteria: 
- Search string.
- Limit date.
- Number of page results. 

Result can be saved in a file. 

## Usage
```
> python getcomics.py [OPTIONS] [SEARCH]

Options:
  --host TEXT        Filter links on specific host.
  --limit-date TEXT  Don't return releases older than this date (format: YYYY-
                     MM-DD).
  --pages INTEGER    Search on the first N pages.
  -o, --output TEXT  Save result to file.
  --help             Show this message and exit.
```

### Command line
You can run the script with all parameters in the commande lines.  

Example :  
```
python -m getcomics --pages 10 --limit-date "2022-09-01" --host ZIPPYSHARE --host MEGA --output output.csv "star wars"
```

This will search for releases corresponding to the search `star wars`.  
Search will be made on the first `10` pages of the website.  
Realses older than `2022-09-01` will be ignored.  
Only links on `ZIPPYSHARE` and `MEGA` will be kept.  
Result will be saved into `output.csv`. 
  
   
### Interactive
You can run the script without any parameters. They will be asked. 
Example :  
```
python -m getcomics
``` 
shows
```
[?] Search for: star wars
Default parameters:
Limit date:          2000-01-01
Limit pages:         1
Filter on host(s):
[?] Keep default parameters?: No
   Yes
 > No

[?] Limit date (default: 2000-01-01): 2022-09-01
[?] How many pages to search (default: 1): 10
[?] Save result to file (default: print in console): output.csv
[?] Filter on host(s):
   o GETCOMICS (14/15)
   o UFILE (14/15)
   X MEGA (11/15)
   o MEDIAFIRE (14/15)
   X ZIPPYSHARE (14/15)
   o READ (8/15)
   o MIRROR (1/15)

[?] File already exists. Overwrite?: Yes
 > Yes
   No

Result saved in "output.csv".
```

## Install
```
git clone https://github.com/PhunkyBob/getcomics.git
cd getcomics
python -m venv venv
venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
```