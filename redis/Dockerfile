FROM redis:7-alpine

# Install envsubst for template processing
RUN apk add --no-cache gettext

# Create redis configuration directory
RUN mkdir -p /usr/local/etc/redis

# Copy configuration template
COPY redis.conf.template /usr/local/etc/redis/redis.conf.template

# Create entrypoint script
RUN echo '#!/bin/sh' > /docker-entrypoint.sh && \
    echo 'if [ -f /run/secrets/redis_password ]; then' >> /docker-entrypoint.sh && \
    echo '  export REDIS_PASSWORD=$(cat /run/secrets/redis_password)' >> /docker-entrypoint.sh && \
    echo 'else' >> /docker-entrypoint.sh && \
    echo '  echo "Error: Redis password secret not found"' >> /docker-entrypoint.sh && \
    echo '  exit 1' >> /docker-entrypoint.sh && \
    echo 'fi' >> /docker-entrypoint.sh && \
    echo 'envsubst < /usr/local/etc/redis/redis.conf.template > /usr/local/etc/redis/redis.conf' >> /docker-entrypoint.sh && \
    echo 'exec redis-server /usr/local/etc/redis/redis.conf' >> /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
