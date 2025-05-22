fission env create \
  --name python311-bookworm-slim \
  --builder anzupop/fission-python-builder-3.11-bookworm-slim \
  --image anzupop/fission-python-env-3.11-bookworm-slim:v2

fission env delete --name python311-bookworm-slim

fission env create \
  --name python311-bookworm-slim-sentence-transformers \
  --builder anzupop/fission-python-builder-3.11-bookworm-slim \
  --image anzupop/fission-python-env-3.11-bookworm-slim:sentence_transformers

fission env delete --name python311-bookworm-slim-sentence-transformers

zip -r reddit-harvester.zip .

fission package create \
  --sourcearchive ./reddit-harvester.zip \
  --env python311-bookworm-slim-sentence-transformers \
  --name reddit-harvester \
  --buildcmd './build.sh'

fission package delete --name reddit-harvester

fission fn create \
  --name reddit-harvester \
  --pkg reddit-harvester \
  --env python311-bookworm-slim-sentence-transformers \
  --entrypoint "harvester.main"

fission fn delete --name reddit-harvester

# create a route for manually testing the function
fission route create \
  --url /reddit-harvester \
  --function reddit-harvester \
  --name reddit-harvester \
  --createingress

# set timeout to 3000 seconds (50 minutes)
fission function update \
  --name reddit-harvester \
  --fntimeout 3000

# set a one hour cronjob for the function
fission timer create \
  --name reddit-harvester-hourly-trigger \
  --function reddit-harvester \
  --cron "0 * * * *"

fission timer delete --name reddit-harvester-hourly-trigger
