# ptt-image-crawler

## Overview
ptt-image-crawler is a web crawling tool that crawls images from PTT (a bulletin board system in Taiwan). You can specify the board, pages, path, and even the number of threads you want to use for crawling.

## Installation
Clone this repository:
```
git clone https://github.com/JudeTe/ptt-image-crawler.git
```

Install the required packages:
```
python -m pip install -r requirements.txt
```

## Usage
```
crawler.py [-h] [--board nba] [-i 50 100] [--path C://] [--dir nba] [--thread 10]
```

optional arguments:
*  -h, --help            show the help message and exit  
*  -b `nba`, --board `nba`  specify the board you want to download (default: 'beauty')  
*  -i `50 100`  specify start and end page you want to download in the given board (default: 0 to 1)  
*  -p `C://`, --path `C://`  specify the path for storing the file (default: './')  
*  -d `nba` --dir `nba` specify the directory name for storing the file (default: '{board name}')  
*  -t `8`, --thread `8` specify how many threads to use for running the program. (default: numbers of your core)  


Custom arguments example:
```
python crawler.py -b nba -i 50 100 -p ./ -d nba -t 10
```

P.S. If the number of threads is not specified, the default is to use the number of cores in the current system as the number of threads to be used.

## License
This project is licensed under the MIT License - see the LICENSE.txt file for details.

