FROM python:3.12-slim

WORKDIR /app

# Install build essentials
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Install PDF rendering dependencies (WeasyPrint requirements)
COPY docker/install-pdf-deps.sh /tmp/
RUN chmod +x /tmp/install-pdf-deps.sh && \
    /tmp/install-pdf-deps.sh && \
    rm -f /tmp/install-pdf-deps.sh


COPY tripPlanService/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY tripPlanService/ /app/

# Setup fonts
COPY docker/setup-fonts.sh /tmp/
RUN chmod +x /tmp/setup-fonts.sh && \
    /tmp/setup-fonts.sh && \
    rm -f /tmp/setup-fonts.sh

COPY docker/entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 50051

ENTRYPOINT ["entrypoint.sh"]
