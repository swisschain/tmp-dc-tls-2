FROM swisschains/kubectl-docker:1.0.4

COPY my_kubernetes.py /my_kubernetes.py
COPY entrypoint.py /entrypoint.py
RUN chmod +x /entrypoint.py

ENTRYPOINT ["/entrypoint.py"]
