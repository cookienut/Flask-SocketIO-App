FROM python:3.6

# Create app directory
WORKDIR /mnt/red_server

# Install app dependencies
COPY requirements.txt .

RUN pip install -r requirements.txt

# Bundle app source
COPY src/ /mnt/red_server/

EXPOSE 6000
EXPOSE 7000
CMD [ "python", "." ]


# docker build -t "red_server_image" .
# docker run --name red_server_container red_server_image

# docker ps -a
# docker container rm <ID>
# docker images
# docker image rm <ID>
