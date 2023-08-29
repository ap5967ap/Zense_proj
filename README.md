
# GoldPulse

A personal finance manager built for Zense recruitment. People can manage incomes, expenses (wants and needs), investments. This bot helps to prioritize your wants and manage accordingly. This bot also gives investments advices and manages income accordingly from both active and passive sources.





## Installation
 A. Fork the repository

```bash
git clone https://github.com/ap5967ap/Zense_proj.git
```

B. Install and Start the Virtual Environment

```bash
python -m venv .
.\Scripts\activate
```
    
C. Install Dependencies
```bash
pip install -r .\requirements.txt
```


D. Migrate Models and Start the Server
```bash
python .\manage.py migrate
python .\manage.py runserver        
```



## Documentation

[Documentation](https://github.com/ap5967ap/Zense_proj/blob/main/Report.pdf)


## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`SECRET_KEY = YOUR_DJANGO_SECRET_KEY`

`DEBUG=DEBUG`

`EMAIL_FROM = YOUR_ADMIN_EMAIL`

`EMAIL_HOST_USER = YOUR_ADMIN_EMAIL`

`EMAIL_HOST_PASSWORD = YOUR_ADMIN_EMAIL_PASSWORD`

`EMAIL_PORT = YOUR_ADMIN_EMAIL_PORT`

`EMAIL_HOST = YOUR_ADMIN_EMAIL_SMTP_HOST`

`PASSWORD_RESET_TIMEOUT = TIMEOUT_FOR_EMAIL_LINKS`


## Authors

- [@ap5967ap](https://www.github.com/ap5967ap)

