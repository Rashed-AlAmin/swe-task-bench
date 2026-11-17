# Sealed environment for reproducing the benchmark.
# The host venv is pinned to the same pytest; this image removes the
# "works on my machine" caveat noted in the README.
FROM python:3.14-slim
RUN pip install --no-cache-dir "pytest==9.2.0"
WORKDIR /bench
COPY scripts/ /bench/scripts/
COPY tasks/   /bench/tasks/
# The click checkout is mounted, not baked, so the image stays small and the
# task base commits stay auditable against upstream.
#   docker run --rm -v "$PWD/repo:/bench/repo" swe-task-bench scripts/controls.sh 3299
ENV PYTHONDONTWRITEBYTECODE=1
ENTRYPOINT ["/bin/sh","-c"]
