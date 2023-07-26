FROM python:3.8.16-slim-buster
EXPOSE 8000
MAINTAINER theolyu
ENV PYTHONPATH "${PYTHONPATH}:/home/DjangoApschedulerDemo/"
WORKDIR /home/DjangoApschedulerDemo/
ADD . /home/DjangoApschedulerDemo
RUN rm /etc/localtime \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && python3 -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ \
    && mkdir /home/DjangoApschedulerDemo/log \
    && chmod +x /home/DjangoApschedulerDemo/run.sh
ENTRYPOINT ["/home/DjangoApschedulerDemo/run.sh"]