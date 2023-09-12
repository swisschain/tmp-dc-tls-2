#!/bin/bash

# exit when any command fails
set -e

echo get kube config
echo "$KUBE_CONFIG_DATA" | base64 -d > /tmp/config
export KUBECONFIG=/tmp/config
echo get kube nodes
kubectl get nodes
rm $KUBECONFIG
