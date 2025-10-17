require 'net/http'
require 'json'

class SubmissionsController < ApplicationController
  def new
    last = session[:last_submission]
    if last
      @text_a = last['text_a'] || last[:text_a]
      @text_b = last['text_b'] || last[:text_b]
      @analyzer = (last['analyzer'] || last[:analyzer] || 'word')
      range = last['ngram_range'] || last[:ngram_range] || [1, 2]
      @ngram_min, @ngram_max = range
      @a_from_file = last['a_from_file'] || last[:a_from_file]
      @b_from_file = last['b_from_file'] || last[:b_from_file]

      # If previous inputs came from files, do NOT prefill the textareas
      @text_a = '' if @a_from_file
      @text_b = '' if @b_from_file
    else
      # defaults
      @analyzer = 'word'
      @ngram_min = 1
      @ngram_max = 2
    end
  end

  def create
  @text_a = extract_text(params, :text_a, :file_a)
  @text_b = extract_text(params, :text_b, :file_b)

    if @text_a.blank? || @text_b.blank?
      flash.now[:alert] = 'Preencha os dois campos de texto antes de comparar.'
      render :new, status: :unprocessable_entity
      return
    end

    analyzer = params.dig(:submission, :analyzer).presence || 'word'
    ngram_min = params.dig(:submission, :ngram_min).presence || '1'
    ngram_max = params.dig(:submission, :ngram_max).presence || '2'
    a_from_file = params.dig(:submission, :file_a).present?
    b_from_file = params.dig(:submission, :file_b).present?
  api_response = request_similarity(@text_a, @text_b, analyzer: analyzer, ngram_range: [ngram_min.to_i, ngram_max.to_i])
  @similarity = api_response.fetch('similarity')
  @is_plagiarism = api_response.fetch('is_plagiarism')
  @matches = api_response.fetch('matches', [])
  @analyzer = api_response['analyzer']
  @ngram_range = api_response['ngram_range']
  @passages = api_response.fetch('passages', [])
  @explanations = api_response.fetch('explanations', [])
    # Persist a SMALL preview for prefilling the next form (avoid cookie overflow)
    a_filename = params.dig(:submission, :file_a)&.original_filename
    b_filename = params.dig(:submission, :file_b)&.original_filename
    # Do not store large text in session; for file uploads, keep fields empty on next load
    preview_a = a_from_file ? '' : truncate_for_session(@text_a)
    preview_b = b_from_file ? '' : truncate_for_session(@text_b)

    session[:last_submission] = {
      text_a: preview_a,
      text_b: preview_b,
      analyzer: @analyzer,
      ngram_range: @ngram_range,
      a_from_file: a_from_file,
      b_from_file: b_from_file
    }
    render :result
  rescue JSON::ParserError, RuntimeError => e
    Rails.logger.error("Plagiarism API error: #{e.message}")
    flash.now[:alert] = 'Não foi possível analisar os textos. Verifique o backend e tente novamente.'
    render :new, status: :bad_gateway
  end

  private

  def extract_text(params, text_key, file_key)
    text = params.dig(:submission, text_key)
    return text.to_s if text.present?

    uploaded = params.dig(:submission, file_key)
    return '' unless uploaded

    # Try to handle PDFs and plain text files gracefully.
    content_type = uploaded.content_type.to_s
    filename = uploaded.original_filename.to_s
    tempfile_path = uploaded.tempfile.path

    if content_type == 'application/pdf' || File.extname(filename).downcase == '.pdf'
      begin
        return extract_pdf_text(tempfile_path)
      rescue => e
        Rails.logger.warn("PDF extraction failed: #{e.class} - #{e.message}")
        # Fallback: return empty string to trigger validation message
        return ''
      end
    end

    # For other text-like uploads (.txt, .tex, etc.) ensure valid UTF-8
    begin
      raw = uploaded.read
      return ensure_utf8(raw)
    rescue => e
      Rails.logger.warn("Upload read/encoding failed: #{e.class} - #{e.message}")
      return ''
    end
  end

  def extract_pdf_text(path)
    # Lazy-require so the app boots even before the gem is installed
    begin
      require 'pdf/reader'
    rescue LoadError
      # Some environments expose the gem under this require path
      require 'pdf-reader'
    end
    text_chunks = []
    PDF::Reader.open(path) do |reader|
      reader.pages.each do |page|
        # Some PDFs may return non-UTF data; normalize after join
        text_chunks << page.text.to_s
      end
    end
    raw = text_chunks.join("\n\n")
    # Clean soft hyphens and common hyphenation linebreaks, normalize spacing
    cleaned = raw
      .gsub(/\u00AD/, '')        # soft hyphen
      .gsub(/-\n\s*/, '')       # hyphenation at line end
      .gsub(/\r/, '')
      .gsub(/[ \t]+/, ' ')
      .gsub(/\n{3,}/, "\n\n")
    ensure_utf8(cleaned)
  end

  def ensure_utf8(str)
    # Convert binary or mixed-encoding strings to valid UTF-8 without raising
    str.to_s.encode('UTF-8', 'binary', invalid: :replace, undef: :replace, replace: '')
  end

  def truncate_for_session(str, max_bytes: 800)
    s = ensure_utf8(str.to_s)
    return s if s.bytesize <= max_bytes
    trimmed = s.byteslice(0, max_bytes)
    ensure_utf8(trimmed) + "… (truncado)"
  end

  def request_similarity(text_a, text_b, analyzer:, ngram_range:)
    uri = URI.parse(ENV.fetch('PLAGIARISM_API_URL', 'http://127.0.0.1:5000/api/compare'))
    http = Net::HTTP.new(uri.host, uri.port)
    http.use_ssl = uri.scheme == 'https'

    request = Net::HTTP::Post.new(uri.request_uri, 'Content-Type' => 'application/json')
    request.body = { text_a:, text_b:, analyzer:, ngram_range: }.to_json

    response = http.request(request)
    raise RuntimeError, "HTTP #{response.code}" unless response.is_a?(Net::HTTPSuccess)

    JSON.parse(response.body)
  end
end