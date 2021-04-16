FROM quay.io/pypa/manylinux1_x86_64

ADD docker/setup.sh /root/setup.sh
ADD docker/test.sh /root/test.sh
COPY . /project

WORKDIR /project

RUN /root/setup.sh  # install cython on all pythons.

ENV PATH=/opt/python/cp27-cp27mu/bin:${PATH}

RUN pip install cget cmake
RUN cget init --std=c++11 --shared -p /cget
RUN cget install --file=native_requirements.txt -p /cget

ENTRYPOINT /root/test.sh
