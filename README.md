<h1>Установить python и pip на сервер</h1>


<h3>1. Установка python</h3>

sudo apt update

sudo apt install software-properties-common

sudo add-apt-repository ppa:deadsnakes/ppa

Press [ENTER] to continue or Ctrl-c to cancel adding it.

sudo apt install python3.10

<h3>2. Установка pip и virtualenv</h3>

python3.8 -m pip install --upgrade pip

pip --version

pip install virtualenv

<h1>Перенос проекта на сервер</h3>

<h3>1. Клонирование репозитория:</h3>

git clone https://github.com/negodinaarina/bot.git

<h3>2. Создание venv</h3>

cd bot 

python3 -m venv /bot

source venv/bin/activate

<h3>3. Установка зависимостей</h3>

pip install -r requirements.txt

cd bot

python main.py


