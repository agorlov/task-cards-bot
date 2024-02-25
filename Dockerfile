# Use the official image as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN pip install pyTelegramBotAPI psycopg2 python-dateutil git+https://github.com/agorlov/whispercpp.py

# Install cron
RUN apt-get update && apt-get -y install cron ffmpeg

COPY cronjob /etc/cron.d/cronjob

COPY ggml-small.bin /root/.ggml-models/ggml-small.bin

# Give execution rights on the cron job and create the log file
RUN chmod 0644 /etc/cron.d/cronjob && touch /var/log/cron.log

# Странный баг, что крон не работает без этого в timeweb
# https://stackoverflow.com/questions/43323754/cannot-make-remove-an-entry-for-the-specified-session-cron
RUN sed -i '/session    required     pam_loginuid.so/c\#session    required   pam_loginuid.so' /etc/pam.d/cron

# Run bot.py and cronjob
CMD python bot.py



