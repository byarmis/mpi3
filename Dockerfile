FROM byarmis/papirus
LABEL maintainer="Ben Yarmis <ben@yarm.is>"

COPY . /mpi3
RUN pip3 install -e /mpi3/

ENTRYPOINT ["python3", "-m", "mpi3"]
CMD ["--help"]

