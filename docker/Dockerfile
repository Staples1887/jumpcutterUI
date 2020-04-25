FROM python:3

RUN apt-get -y update && apt-get -y install ffmpeg imagemagick \
    libopencv-dev python-opencv git python-dev libsdl-image1.2-dev \
    libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsdl1.2-dev libsmpeg-dev \
    python-numpy subversion libportmidi-dev ffmpeg libswscale-dev libavformat-dev libavcodec-dev

RUN apt-get -y install fonts-liberation

RUN apt-get install -y locales && \
    locale-gen C.UTF-8 && \
    /usr/sbin/update-locale LANG=C.UTF-8

ENV LC_ALL C.UTF-8

RUN pip install imageio numpy scipy matplotlib pandas sympy nose decorator proglog pillow pytest requests pygame moviepy==1.0.0
RUN pip install scikit-image sklearn
RUN cat /etc/ImageMagick-6/policy.xml | sed 's/none/read,write/g'> /etc/ImageMagick-6/policy.xml 

WORKDIR /home
