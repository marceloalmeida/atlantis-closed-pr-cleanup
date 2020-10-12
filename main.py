import python_jwt as jwt, jwcrypto.jwk as jwk, datetime
import requests
from os import listdir, getenv
from shutil import rmtree
from json import dumps
import logging

logger = logging.getLogger('atlantis-closed-pr-cleanup')
hdlr = logging.FileHandler(getenv("LOG_FILENAME", "/dev/stdout"))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

git_providers=["github.com"]
accept_header="application/vnd.github.v3+json"

data_dir=getenv("ATLANTIS_DATA_DIR")
gh_app_key_file=getenv("ATLANTIS_GH_APP_KEY_FILE")
repo_allowlist=getenv("ATLANTIS_REPO_ALLOWLIST").split(",")
gh_app_id=getenv("ATLANTIS_GH_APP_ID")

def get_repository_name(repository):
  return map(lambda git_provider: repository.replace('%s/' % git_provider, ''), git_providers)[0]

def delete_gh_closed_prs(repository, rs):
  f = open(gh_app_key_file, "r")

  priv_key = jwk.JWK.from_pem(f.read())
  payload = { 'iss': gh_app_id };
  token = jwt.generate_jwt(payload, priv_key, 'RS256', datetime.timedelta(minutes=5))

  installation = requests.get(url="https://api.github.com/repos/%s/installation" % repository, headers={"Authorization": "Bearer %s" % token, "Accept": accept_header})

  access_token = requests.post(url="https://api.github.com/app/installations/%s/access_tokens" % installation.json()["id"], data=dumps({"repositories":[repository.split("/")[1]]}), headers={"Authorization": "Bearer %s" % token, "Accept": accept_header})

  for pr in prs:
    pr_state = requests.get(url="https://api.github.com/repos/%s/pulls/%s" % (repository, pr), headers={"Authorization": "token %s" % access_token.json()["token"], "Accept": accept_header})
    if pr_state.json()["state"] in ["closed"]:
      logger.info("Deleted \"%s/repos/%s/%s\"" % (data_dir, repository, pr))
      rmtree("%s/repos/%s/%s" % (data_dir, repository, pr))


for repository in repo_allowlist:
  prs= listdir("%s/repos/%s" % (data_dir, get_repository_name(repository)))
  if repository.startswith("github.com"):
    delete_gh_closed_prs(get_repository_name(repository), prs)
