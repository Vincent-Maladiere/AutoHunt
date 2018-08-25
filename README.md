# AutoHunt - Alpha version

A webscraping solution to collect data from Real Estate agencies.

### Inputs Sheet

Select your research criterias.
You can use keyword on the right to boost, filter or delete results

![alt text](https://raw.githubusercontent.com/Vincent-Maladiere/AutoHunt/master/inputs.png)

### Results Sheet

Watch the results from supported website! (See config for full list of website)

![alt text](https://raw.githubusercontent.com/Vincent-Maladiere/AutoHunt/master/results.png)

## Getting Started

### Prerequisites

• Python version 3.3+ \n
• gspread >=3.0.0 \n
• pandas >=0.20.3 \n
• selenium >=3.11.0 \n
• oauth2client >=4.1.2 \n

### Installing

1. From Github 

```
git clone https://github.com/Vincent-Maladiere/AutoHunt.git
cd AutoHunt
python setup.py install
```

2. Copy the following Google Spreadsheet : https://docs.google.com/spreadsheets/d/1loVeOwRpGh_-he6kQNnj_vtCS4EIuYVg9ucV3id1cmQ/edit#gid=0

3. Follow this tutorial to connect your spreadsheet with your google script account : https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html

Don't forget to share your spreadsheet with your 'name@project-id-xxxx' provided by the operation 2., otherwise you won't be able to find it.

4. Replace 'Your_Apps_Script_Execution.json' file with the file provided by operation 2.

5. At the bottom of config.py, set : 

```
GOOGLE_SPREADSHEET_NAME = 'YOUR GOOGLE SPREADSHEET'
``` 

and 

```
Apps_Script_Credentials = 'YOUR_CREDENTIAL_FILE.json'
```

### Running

```
python3 AutoHunt.py
```

## TODO NEXT

Deploying the project on pythonanywhere or Django to ensure a steady run

## Authors

* **Vincent Maladiere** - *Initial work* - [Vincent-Maladiere](https://github.com/Vincent-Maladiere)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to @Robin900 whose gspread-dataframe under MIT license was used in format.py
