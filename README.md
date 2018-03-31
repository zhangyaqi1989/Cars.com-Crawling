# Crawler for cars.com
A python crawler which can crawl car information from [cars.com](https://www.cars.com). It supports
python 3.6+.
The below libraries are needed.
* Beautiful Soup 4
* pandas
* numpy
* matplotlib

Examples:
1. Cars crawling: crawl cars of a specific model (e.g. Audi Q7) on cars.com and analyze prices.
```
bash crawling.sh
```

2. Multiple crawl: crawl multiple car models listed in a file on cars.com and plot price comparison
```
bash multiple-crawling.sh
```

3. Brand guess game: a command line car brand guessing game
```
bash brand-guess-game.sh
```
