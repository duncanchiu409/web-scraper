FROM python:3.10.4-bullseye

WORKDIR /app

COPY . .

RUN mkdir -p /app/credentials

COPY ./credentials/ ./credentials/

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

RUN unzip awscliv2.zip

RUN ./aws/install

RUN aws configure import --csv file://./credentials/<your_access_key_file>.csv

RUN pip install -r requirements.txt

# CMD ["python", "<your_script>.py"]