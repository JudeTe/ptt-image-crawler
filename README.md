# PttCrawler

## Overview
PttCrawler is a web crawling module used to crawl images from PTT (a bulletin board system in Taiwan). You can specify the board, pages, path, and even the number of threads or processes you want to use for crawling.

## Installation
Clone this repository:
```
git clone https://github.com/JudeTe/PttCrawler.git
```

Install the required packages:
```
python -m pip install -r requirements.txt
```

## Usage
```
crawler.py [-h] [-b nba] [--pages 10] [--path C://] [--dir nba] [-t 10] [-p 4]
```

optional arguments:
*  -h, --help            show the help message and exit  
*  -b `nba`, --board nba  specify the board you want to download (default: 'beauty')  
*  --pages `10`  specify how many pages you want to download in the given board (default: 1)  
*  --path `C://`  specify the path for storing the file (default: './')  
*  --dir `nba` specify the directory name for storing the file (default: '{board name}')  
*  -t 10 thread `10` specify how many threads to use for running the program. (default: 0)  
*  --process `4` specify how many processes to use for running the program. (default: 0)  


Custom arguments example:
```
python crawler.py -b nba --pages 10 --path ./ --dir nba -t 10
```

P.S. If the number of processes and threads is not specified, the default is to use the number of cores in the current system as the number of processes to be used.

## License
This project is licensed under the MIT License - see the LICENSE.txt file for details.

