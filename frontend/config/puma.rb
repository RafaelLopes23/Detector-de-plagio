# Puma configuration for the Rails application

max_threads_count = ENV.fetch("RAILS_MAX_THREADS", 5).to_i
min_threads_count = ENV.fetch("RAILS_MIN_THREADS", max_threads_count).to_i
threads min_threads_count, max_threads_count

port ENV.fetch("PORT", 3000)
environment ENV.fetch("RACK_ENV", "development")

# Use workers only if WEB_CONCURRENCY > 0
worker_count = ENV.fetch("WEB_CONCURRENCY", 0).to_i
if worker_count > 0
  workers worker_count
  preload_app!
end

plugin :tmp_restart
