# Library Management Api

Library management api using fast api


## Features

- Authentication System With Token(JWT)
- User Authorization And Group Management
- Handel Two Many Request
- Block Suspicious Ip
- Handle 2AF Authentication
- Reset Password By Email
- Request With Only allowed Ip option
- Throttling(Request Management)
- Cache Data
- Upload File
- Reporting capability
- Insert Data By Seeder


## Installation

1. Clone the repository

```
Clone git@github.com:mobinghanbari/library-management.git
```

```
cd library-management
```

2. Create a virtualenv

```
python -m venv venv
```

```
venv\Scripts\activate.bat
```

3. Install the requirements

```
pip install -r requirements.txt
```

4. Feel the .env file data requirements


5. Run the below command to create migration

```
 alembic revision --autogenerate -m "initial migration
 ```

6. Running the below command to apply migrations on db

```
alembic upgrade head
```

7. Start redis server
```
redis-server
```

8. Run the below command to seed db
```
python seeder.py
```

9. Run the project
```
fastapi dev main.py
```


## Contact me

## Email: mobinghnbari222@gmail.com
