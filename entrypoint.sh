#!/bin/sh -l

set -e  # stops execution
set -u  # undefined variable

echo "Set git globals"
git config --global user.name "${GIT_USER_NAME}"
git config --global user.email "${GIT_USER_EMAIL}"
clone_commit_push() {
  if [ -d /tmp/git ]; then 
    echo Temp Directory exist - remove
    rm -r /tmp/git;
    echo Create Temp Directory;
    mkdir /tmp/git; 
  else
    echo Create Temp Directory;
    mkdir /tmp/git; 
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
  sleep 30
  echo "Push to git"
  git push
  exit_status=$?
  echo "Changes log"
  git log -2
  echo $exit_status
}
exit_code=$(clone_commit_push)
if [ "$exit_code" -eq 1 ]; then
  echo "Push-Not-Success"
else
  echo "Push-Success"
fi
