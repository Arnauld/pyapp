FROM python:3.6-alpine

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev zsh git curl bash \
    && pip install psycopg2

# ZSH
RUN bash -c "$(wget https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh -O -)"
ADD data/.zshrc /root/.zshrc

VOLUME ["/app"]
WORKDIR /app

CMD ["/bin/zsh"]
