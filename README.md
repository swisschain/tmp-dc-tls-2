# Kubernetes Apply Smart
Apply all changes in commit to kunernetes in a smart way

After creating pool request DRY RUN test will started and after merge reall apply will performed
## Settings
1. Set sequence group in kubernetes yaml file, to deploy it in specific order

Deployment file example
```
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    deployment-order-group: new-group1
  name: new-service
  namespace: new-namespace
spec:
```
2. Specify sequence of group

In pool request comment while creating (you can add ``` before and after list of groups)
```
Some text

~deployment-order
group:new-group1
group:new-group2
group:new-group3

Some text
```

Also you can Specify order in local file ```deployment-order-group-priorities``` at repository
```
group:new-group1
group:new-group2
group:new-group3
```

## Pipelines
1. Start on create or update pool request (try run)
```
name: check-deploy
on:
  pull_request:
    types:
      - labeled
      - unlabeled
      - opened
      - reopened
      - synchronize
jobs:
  check-deploy:
    name: check-deploy
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0
    - name: Check PR
      uses: swisschain/kubeapplysmart@master
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_USER_API_TOKEN }}
        GITHUB_FULL_JSON: ${{ toJSON(github) }}
        KUBE_CONFIG_DATA: ${{ secrets.KUBERNETES_CONFIG }}
        #LOG: DEBUG
        LOG: INFO
        HOSTS_IP: 127.0.0.1
        HOSTS_NAME: localhost-test
        DRY_RUN: True
```

2. Merge pool request (real run)
```
name: deploy
on:
  push:
    branches: [ master ]
jobs:
  deploy:
    name: deploy
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0
    - name: Check PR
      uses: swisschain/kubeapplysmart@master
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_USER_API_TOKEN }}
        GITHUB_FULL_JSON: ${{ toJSON(github) }}
        KUBE_CONFIG_DATA: ${{ secrets.KUBERNETES_CONFIG }}
        #LOG: DEBUG
        LOG: INFO
        HOSTS_IP: 127.0.0.1
        HOSTS_NAME: localhost-test
        DRY_RUN: False
```

