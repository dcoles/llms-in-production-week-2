FROM python:3.10-slim-bullseye

ARG GUARDRAILS_TOKEN
ARG OPENAI_API_KEY

ENV APP_HOME /app
ENV PYTHONPATH=$APP_HOME
ENV GUARDRAILS_TOKEN=$GUARDRAILS_TOKEN
ENV OPENAI_API_KEY=$OPENAI_API_KEY

WORKDIR $APP_HOME

COPY ./requirements.txt /app/requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential gcc git \
  && pip install --no-cache-dir --upgrade -r /app/requirements.txt \
  && guardrails configure --disable-metrics --disable-remote-inferencing --token $GUARDRAILS_TOKEN \
  && guardrails hub install hub://guardrails/valid_sql \
  && guardrails hub install hub://guardrails/valid_json \
  && guardrails hub install hub://guardrails/unusual_prompt \
  && rm -rf /var/lib/apt/lists/*
# Add more guardrails to be installed in this chained RUN command!

COPY src ./src
COPY .streamlit ./.streamlit

EXPOSE 8080

CMD ["streamlit", "run", "src/streamlit_app.py", "--server.port", "8080"]
