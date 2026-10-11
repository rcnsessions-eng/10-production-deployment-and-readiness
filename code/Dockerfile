FROM zero-trust-supply-chain-security-checks:0.1.0
ENV PYTHONPATH=/readiness-scripts:/app/mcp:/app
COPY 10-production-deployment-and-readiness/code/scripts /readiness-scripts
COPY 10-production-deployment-and-readiness/code/tests /readiness-tests
USER 10001:10001
CMD ["python", "-m", "pytest", "-p", "no:cacheprovider", "/readiness-tests", "-q"]