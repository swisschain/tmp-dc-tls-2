FROM swisschains/kubectl-docker:1.0.5

COPY my_git.py /my_git.py
COPY my_github.py /my_github.py
COPY my_yaml.py /my_yaml.py
COPY my_kubernetes.py /my_kubernetes.py
COPY entrypoint.py /entrypoint.py
RUN chmod +x /entrypoint.py

ENTRYPOINT ["/entrypoint.py"]
