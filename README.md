## OPROSIKI 🧩
A platform for creating surveys and also analyze the results – in real time.

## What is Oprosiki?
А platform for creating your own surveys on any topic.
The ability to participate in user surveys and view the results in real time.
Selection of surveys specifically for you, based on your actions.


## Installation

1. Cloning a repository

```git clone https://github.com/repulsiveone/oprosiki.git```

2. Install requirements

 ```pip3 install -r requirements.txt```
 
3. Going to the directory src

```cd src```

4. Application launch

```python3 manage.py runserver```

5. Launch Celery

If you use Windows:
```celery -A config worker --loglevel=info -P eventlet```

*Need for the recommendation system.*

*Configure redis and celery in the file settings.py* !!!

For the application to work correctly, you also need to create a file src/config/config_info.py in which to set up: 
- django secret key
- postgresql config
- email config

## Preview
<p align="center">
  <img src="https://github.com/user-attachments/assets/156e5bcf-19a5-4402-bbf6-eed111609020" width="45%" />
  <img src="https://github.com/user-attachments/assets/0f3105fb-8e27-450a-aa2c-0cd6af7f292c" width="45%" />
  <img src="https://github.com/user-attachments/assets/0ade7ba4-df58-47cb-a5ae-ea80b4af8096" width="45%" />
  <img src="https://github.com/user-attachments/assets/c3b331d9-ffc4-4e79-b9c6-f894570e968b" width="45%" />
</p>
