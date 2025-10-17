Rails.application.routes.draw do
  root to: 'submissions#new'
  post '/compare', to: 'submissions#create', as: :compare_texts
end