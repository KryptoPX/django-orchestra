FROM debian:latest as base

RUN apt update -y && apt upgrade -y
RUN apt-get install --no-install-recommends -y git python python3-pip python3-venv curl
RUN python3 -m pip install --upgrade pip
RUN pip3 install wheel

# contenedor orchestra
FROM base as orchestra
RUN useradd -m orchestra
USER orchestra
WORKDIR /home/orchestra
RUN python3 -m venv env
RUN echo ". /home/orchestra/env/bin/activate" > ~/.bashrc
RUN chmod +x ~/.bashrc
RUN . env/bin/activate

RUN python3 -m pip install --upgrade pip setuptools\<58
RUN curl https://raw.githubusercontent.com/ribaguifi/django-orchestra/master/requirements.txt -o req-orchestra.txt
RUN pip3 install -r req-orchestra.txt


# contenedor musician
FROM base as musician
RUN useradd -m musician
USER musician
WORKDIR /home/musician
RUN python3 -m venv env
RUN echo ". /home/musician/env/bin/activate" > ~/.bashrc
RUN chmod +x ~/.bashrc
RUN . env/bin/activate

RUN python3 -m pip install --upgrade pip setuptools
RUN curl https://raw.githubusercontent.com/ribaguifi/django-musician/master/requirements.txt -o req-musician.txt
RUN pip3 install -r req-musician.txt