require "active_support/core_ext/integer/time"

Rails.application.configure do
  config.cache_classes = false
  config.eager_load = false
  config.consider_all_requests_local = true
  config.server_timing = true

  config.public_file_server.enabled = true
  config.assets.debug = true
  config.assets.quiet = true

  config.log_level = :debug
  config.log_tags = [:request_id]

  config.action_controller.perform_caching = false
  config.cache_store = :null_store

  config.active_support.deprecation = :log
  config.active_support.disallowed_deprecation = :raise
  config.active_support.disallowed_deprecation_warnings = []

  config.hosts.clear
end
