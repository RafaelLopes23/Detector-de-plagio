require "active_support/core_ext/integer/time"

Rails.application.configure do
  config.cache_classes = true
  config.eager_load = true
  config.consider_all_requests_local = false
  config.public_file_server.enabled = ENV['RAILS_SERVE_STATIC_FILES'].present?
  # Enable on-the-fly asset compilation for this lightweight deployment.
  # Our app only uses a small CSS file; this avoids build-time precompile requirements.
  config.assets.compile = true
  config.log_level = :info
  config.log_tags = [:request_id]

  config.i18n.fallbacks = true
  config.active_support.report_deprecations = false

  config.force_ssl = false
end
