cd /home/_a1/u-ml-api
. venv/bin/activate
python -m aiohttp.web -H localhost -P 8080 api.main:init