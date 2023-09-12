#!/bin/sh -l

#set -e  # stops execution
set -u  # undefined variable

echo "Set git globals"
git config --global user.name "${GIT_USER_NAME}"
git config --global user.email "${GIT_USER_EMAIL}"
clone_commit_push() {
  (
  if [ -d /tmp/git ]; then 
    echo Temp Directory exist - remove
    rm -r /tmp/git
    echo Create New Temp Directory
    mkdir /tmp/git
  else
    echo Create Temp Directory
    mkdir /tmp/git
  fi
  echo "Cloning git repository"
  git clone --single-branch --branch "$GIT_INFRASTRUCTURE_REPOSITORY_BRANCH" "https://x-access-token:$GIT_USER_API_TOKEN@github.com/$GIT_INFRASTRUCTURE_REPOSITORY_OWNER/$GIT_INFRASTRUCTURE_REPOSITORY_NAME.git" /tmp/git
  echo "Go to git repository dir"
  cd /tmp/git
  #
  echo "Set tag"
  TAG=$(echo ${GITHUB_REF} | sed -e "s/refs\/tags\/${INPUT_TAG_NAME_SKIP}//")
  echo "Set docker image"
  DOCKER_IMAGE=$(printf "%s/%s" $DOCKER_REPOSITORY_NAME $DOCKER_IMAGE_NAME)
  echo DOCKER_IMAGE=$DOCKER_IMAGE
  echo "Set docker image with slash"
  DOCKER_IMAGE_SLASH=$(echo ${DOCKER_IMAGE} | sed 's#/#\\/#g')
  echo DOCKER_IMAGE_SLASH=${DOCKER_IMAGE_SLASH}
  #
  echo "Start processing"
  for YAML_FILE in $(grep -rn $DOCKER_IMAGE: ./ | awk -F: '{print $1}')
  do
    echo Processing $YAML_FILE
    sed -E "s/${DOCKER_IMAGE_SLASH}:.+$/${DOCKER_IMAGE_SLASH}:${TAG}/" ${YAML_FILE} > ${YAML_FILE}.tmp
    echo "Rename temp file" 
    mv ${YAML_FILE}.tmp ${YAML_FILE}
  done
  #
  echo "Add changed file to git"
  git add -A
  echo "Show changes"
  git diff --cached
  echo "Commit to git"
  git commit -m "$GIT_REPOSITORY_NAME ${TAG}"
  echo Sleep 30
  sleep 60
  echo "Push to git"
  git push
  echo $? > /tmp/exit_status
  echo "Changes log"
  git log -2
  ) > /tmp/clone_commit_push.log 2>&1
}
clone_commit_push
exit_code=$(cat /tmp/exit_status)
if [ "$exit_code" -eq 1 ]; then
  echo "Print Log F1"
  cat /tmp/clone_commit_push.log
  echo "Push-Not-Success try again"
  clone_commit_push
  exit_code_2=$(cat /tmp/exit_status)
  if [ "$exit_code_2" -eq 1 ]; then
    echo "Print Log F2"
    cat /tmp/clone_commit_push.log
    echo "Push-Not-Success"
    exit 1
  fi
else
  echo "Print Log S1"
  cat /tmp/clone_commit_push.log
  echo "Push-Success"
  exit 0
fi
