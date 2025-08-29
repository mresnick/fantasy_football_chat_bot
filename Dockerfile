FROM python:3.9.9-slim-bullseye

# Install app
ADD . /usr/src/gamedaybot
WORKDIR /usr/src/gamedaybot

# Install dependencies using pip with better dependency resolution
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -e .

# Launch app
CMD ["python3", "gamedaybot/espn/espn_bot.py"]