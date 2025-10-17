# syntax=docker/dockerfile:1
FROM ruby:3.4-slim

ENV RAILS_ENV=production \
    RACK_ENV=production \
    BUNDLER_WITHOUT="development:test" \
    BUNDLE_PATH=/usr/local/bundle

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    nodejs \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install gems
COPY Gemfile Gemfile.lock /app/
RUN bundle config set without 'development test' \
 && bundle install --jobs 4 --retry 3

# Copy app
COPY . /app

# Environment
ENV PORT=3000 \
    RAILS_SERVE_STATIC_FILES=true \
    WEB_CONCURRENCY=1 \
    RAILS_LOG_TO_STDOUT=true

EXPOSE 3000

# Precompile assets if needed (no DB)
RUN bundle exec rake assets:precompile || true

# Add script to handle cleanup before starting
RUN echo '#!/bin/sh\nrm -f tmp/pids/server.pid\nexec "$@"' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["bundle", "exec", "puma", "-C", "config/puma.rb"]
