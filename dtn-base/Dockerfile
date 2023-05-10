#this docker file builds the image for the node that
#features dtn

FROM ubuntu:22.04

ENV NODE_ID=
ENV NODE_LOCAL_IP=
ENV NODE_ENDPOINT= 


WORKDIR /node

COPY ./dtn7-go/ /node

#start node
CMD ["sh", "start.sh"]

# --- For debugging purposes ---
#CMD ["tail", "-f", "/dev/null"]


