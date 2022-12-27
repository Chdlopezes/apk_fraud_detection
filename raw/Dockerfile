FROM python:3.10-slim

ENV DEBIAN_FRONTEND noninteractive
ENV GECKODRIVER_VER v0.30.0
ENV FIREFOX_VER 96.0.2

# Needed to opencv to work
RUN apt-get update && apt-get install -y libgl1 libsm6 libxext6 libxrender-dev ffmpeg build-essential curl


WORKDIR /raw
# Install requirements
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

CMD ["python3", "-m", "src.comparisson_client"]
