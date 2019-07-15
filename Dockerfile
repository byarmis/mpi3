FROM byarmis/papirus
LABEL maintainer="Ben Yarmis <ben@yarm.is>"

COPY requirements.txt /mpi3/requirements.txt
RUN pip3 install -r /mpi3/requirements.txt

COPY . /mpi3
RUN pip3 install -e /mpi3/

ENTRYPOINT ["python3", "-m", "mpi3"]
CMD ["--help"]