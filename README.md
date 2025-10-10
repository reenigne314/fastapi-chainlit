# fastapi-chainlit

connecting chainlit with temporary memory

Refer graph folder for understanding the langgraph implementation of short term memory using langraph + sqllite

Refer chat-agent folder for implementation of chainlit - the UI for short term memory based langraph

Finally fastapi is used for deploying chainlit app

<img src="./pictures/screenshot.png" width="400" alt="My App Screenshot">

Steps for running the file

Step-1:

```bash

git pull https://github.com/reenigne314/fastapi-chainlit.git

```

Step-2: Create a venv and activate

```bash

uv venv && source .venv/bin/activate

```

Step-3: download the requirements

```bash

uv pip install -r requirements.txt

```

Step-4:

Option-1: Run the chainlit app directly

```bash

cd chainlit && chainlit run chainlit-chat.py -w

```

Option-2: Run using fastapi

```bash

uvicorn fastapi/main:app --reload

```
