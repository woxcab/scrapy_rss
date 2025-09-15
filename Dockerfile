FROM alpine:3.10 AS py27
ARG UNAME
ARG USERID
ARG GROUPID
ARG WORKDIR
RUN apk update && apk add build-base libffi-dev openssl-dev python2 python2-dev py2-pip py2-lxml tzdata && \
    addgroup -g $GROUPID $UNAME && \
    adduser -u $USERID -S -s /bin/sh $UNAME $UNAME && \
    pip install --disable-pip-version-check tox
USER $UNAME
WORKDIR $WORKDIR


FROM python:3.3-alpine AS py33
ARG UNAME
ARG USERID
ARG GROUPID
ARG WORKDIR
RUN apk update && apk add build-base libffi-dev openssl-dev libxml2 libxml2-dev libxslt-dev tzdata && \
    addgroup -g $GROUPID $UNAME && \
    adduser -u $USERID -S -s /bin/sh $UNAME $UNAME && \
    pip3 install --disable-pip-version-check -U pip==10.0.1 incremental==17.5.0 setuptools==39.2.0 wheel==0.29.0 cffi==1.12.3 pycparser==2.14 && \
    pip3 install --disable-pip-version-check tox==2.9.1 virtualenv==15.2.0 py==1.4.34 packaging==16.8 Automat==0.7.0 PyDispatcher==2.0.5 PyHamcrest==1.8.5 Twisted==17.9.0 asn1crypto==0.24.0 attrs==18.2.0 constantly==15.1.0 coverage==4.5.3 cryptography==1.9 cssselect==1.0.1 frozendict==1.2 hyperlink==19.0.0 idna==2.7 lxml==4.2.6 nose==1.3.7 parsel==1.2.0 py==1.4.34 pyOpenSSL==16.2.0 pyasn1==0.4.5 pyasn1-modules==0.2.5 pytest==3.2.5 pytest-cov==2.5.1 python-dateutil==2.9.0.post0 queuelib==1.5.0 service-identity==14.0.0 six==1.12.0 w3lib==1.19.0 xmlunittest==0.5.0 zope.interface==4.4.3
USER $UNAME
WORKDIR $WORKDIR


FROM ubuntu:trusty AS py34
ADD https://bootstrap.pypa.io/pip/3.4/get-pip.py /get-pip.py
ENV DEBIAN_FRONTEND=noninteractive
ARG UNAME
ARG USERID
ARG GROUPID
ARG WORKDIR
RUN apt-get update && \
    locale-gen en_US.UTF-8 && \
    apt-get install -y libffi-dev libssl-dev python3 python3-dev python3-lxml && \
    groupadd -g $GROUPID -o $UNAME && \
    useradd -m -u $USERID -g $GROUPID -o -s /bin/bash $UNAME
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8
RUN python3 get-pip.py --no-setuptools --no-wheel "pip < 19.2" && rm -f get-pip.py && \
    pip3 install --disable-pip-version-check incremental==17.5.0 setuptools==39.2.0 && \
    pip3 install --disable-pip-version-check tox==3.8.3 virtualenv==16.0.0 filelock==3.0.12 py==1.8.0 pluggy==0.12.0 pyparsing==2.4.1.1 packaging==19.0 importlib-resources==1.0.2 importlib-metadata==0.18 pathlib2==2.3.4 Automat==0.7.0 apipkg==1.5 PyDispatcher==2.0.5 PyHamcrest==1.9.0 Twisted==19.2.0 asn1crypto==0.24.0 atomicwrites==1.3.0 attrs==19.1.0 cffi==1.12.3 constantly==15.1.0 coverage==4.5.3 cryptography==2.7 cssselect==1.0.3 frozendict==1.2 hyperlink==19.0.0 idna==2.8 more-itertools==7.2.0 parsel==1.5.1 pyOpenSSL==19.0.0 pyasn1==0.4.5 pyasn1-modules==0.2.5 pytest==4.6.4 pytest-cov==2.7.1 python-dateutil==2.9.0.post0 queuelib==1.5.0 scandir==1.10.0 service-identity==18.1.0 six==1.12.0 w3lib==1.20.0 wcwidth==0.1.7 xmlunittest==0.5.0 zipp==0.5.2 zope.interface==4.6.0
USER $UNAME
WORKDIR $WORKDIR


FROM alpine:3.5 AS py35
ADD https://bootstrap.pypa.io/pip/3.5/get-pip.py /get-pip.py
ARG UNAME
ARG USERID
ARG GROUPID
ARG WORKDIR
RUN apk update && \
    apk add build-base python3 python3-dev openssl-dev py3-lxml libffi-dev tzdata && \
    addgroup -g $GROUPID $UNAME && \
    adduser -u $USERID -S -s /bin/sh $UNAME $UNAME 
RUN python3 get-pip.py --no-setuptools --no-wheel "pip < 21" && rm -f get-pip.py && \
    pip3 install --disable-pip-version-check setuptools==39.2.0 && \
    pip3 install --disable-pip-version-check cryptography==3.2.1 distlib==0.3.7 filelock==3.2.1 idna==2.2 importlib-metadata==2.1.3 importlib-resources==3.2.1 lxml==3.6.4 packaging==20.9 platformdirs==2.0.2 pluggy==0.13.1 py==1.4.31 pyasn1==0.1.9 pycparser==2.14 pyparsing==2.4.7 pytest==3.0.3 python-dateutil==2.8.2 six==1.16.0 toml==0.10.2 tox==3.28.0 virtualenv==20.15.1 zipp==1.2.0 wheel==0.37.1
USER $UNAME
WORKDIR $WORKDIR


FROM alpine:3.9 AS py36
ARG UNAME
ARG USERID
ARG GROUPID
ARG WORKDIR
RUN apk update && \
    apk add build-base python3 python3-dev openssl-dev py3-lxml py3-cryptography py3-cffi libffi-dev py3-pytest tzdata &&  \
    addgroup -g $GROUPID $UNAME && \
    adduser -u $USERID -S -s /bin/sh $UNAME $UNAME
RUN pip3 install --disable-pip-version-check tox
USER $UNAME
WORKDIR $WORKDIR


FROM alpine:3.10 AS py37
ARG UNAME
ARG USERID
ARG GROUPID
ARG WORKDIR
RUN apk update && \
    apk add build-base curl cargo python3 python3-dev openssl-dev py3-lxml py3-cryptography py3-cffi libffi-dev py3-openssl tzdata &&  \
    addgroup -g $GROUPID $UNAME && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    adduser -u $USERID -S -s /bin/sh $UNAME $UNAME
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
USER root
RUN pip3 install --disable-pip-version-check setuptools==47.3.1 wheel==0.42.0 && \
    pip3 install --disable-pip-version-check attrs==19.2.0 Automat==20.2.0 PyDispatcher==2.0.5 Twisted==21.2.0 apipkg==1.5 constantly==15.1.0 coverage==7.2.7 cssselect==1.1.0 cryptography==3.4.6 execnet==1.8.0 exceptiongroup==1.2.2 frozendict==1.2 h2==3.2.0 hpack==3.0.0 hyperframe==5.2.0 hyperlink==21.0.0 importlib-metadata==6.7.0 incremental==21.3.0 iniconfig==1.1.1 itemadapter==0.2.0 itemloaders==1.0.4 jmespath==0.10.0 packaging==23.2 parameterized==0.8.1 parsel==1.6.0 priority==1.3.0 protego==0.1.16 pyasn1==0.4.8 pyasn1-modules==0.2.8 pyOpenSSL==21.0.0 pyparsing==2.4.7 pytest-cov==4.1.0 pytest-forked==1.3.0 pytest-xdist==2.2.1 pytest-asyncio==0.21.2 queuelib==1.5.0 service-identity==18.1.0 toml==0.10.2 typing-extensions==4.7.1 w3lib==1.22.0 xmlunittest==0.5.0 zipp==3.4.1 zope.interface==5.3.0 pyproject-api==1.5.3 platformdirs==3.11.0 virtualenv==20.26.6 tox==4.8.0
USER $UNAME
WORKDIR $WORKDIR


FROM alpine:3.13 AS py38
ADD https://bootstrap.pypa.io/pip/3.5/get-pip.py /get-pip.py
ARG UNAME
ARG USERID
ARG GROUPID
ARG WORKDIR
RUN apk update && \
    apk add build-base python3 python3-dev openssl-dev py3-lxml py3-cryptography py3-cffi libffi-dev tzdata &&  \
    addgroup -g $GROUPID $UNAME && \
    adduser -u $USERID -S -s /bin/sh $UNAME $UNAME
RUN python3 get-pip.py --no-setuptools --no-wheel "pip < 25" && rm -f get-pip.py && \
    pip3 install --disable-pip-version-check tox
USER $UNAME
WORKDIR $WORKDIR


FROM alpine:3.19 AS py3
ARG UNAME
ARG USERID
ARG GROUPID
ARG WORKDIR
RUN apk update && \
    apk add curl git bash build-base libffi-dev openssl-dev bzip2-dev zlib-dev xz-dev readline-dev sqlite-dev tzdata && \
    addgroup -g $GROUPID $UNAME && \
    adduser -u $USERID -S -s /bin/bash $UNAME $UNAME && \
    printf $'#!/bin/bash\n\
default=(echo "Nothing to execute")\n\
str=$(printf \'"%%s" \' "${@:-${default[@]}}")\n\
/bin/bash -lc "$str"\n' > /bin/runcmd && \
    chmod +x /bin/runcmd
USER $UNAME
WORKDIR $WORKDIR
SHELL ["/bin/bash", "-lc"]
RUN git clone https://github.com/pyenv/pyenv.git ~/.pyenv && \
    cd ~/.pyenv && src/configure && make -C src && \
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.profile && \
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.profile && \
    echo 'eval "$(pyenv init --path)"' >> ~/.profile && \
    echo 'eval "$(pyenv init -)"' >> ~/.profile && \
    source ~/.profile && \
    for v in 3.9 3.10 3.11 3.12 3.13; do pyenv install "$v:latest"; done && \
    pyenv versions --bare | tee ~/.pyenv/version .python-version && \
    for v in 3.9 3.10 3.11 3.12 3.13; do pip$v install -U pip; done && \
    pip3.9 install tox
ENTRYPOINT ["/bin/runcmd"]
CMD ["echo", "py3 is built"]


FROM fedora:latest AS py314
ADD https://bootstrap.pypa.io/get-pip.py /get-pip.py
ARG UNAME
ARG USERID
ARG GROUPID
ARG WORKDIR
RUN dnf -y update && \
    dnf -y install make automake gcc gcc-c++ glibc-langpack-en kernel-devel gnupg ca-certificates libffi-devel libxml2-devel libxslt-devel python3.14 python3.14-devel && \
    python3.14 /get-pip.py && rm -f /get-pip.py && \
    groupadd -g $GROUPID -o $UNAME && \
    useradd -m -u $USERID -g $GROUPID -s /bin/bash $UNAME
RUN pip install --disable-pip-version-check tox
USER $UNAME
WORKDIR $WORKDIR
