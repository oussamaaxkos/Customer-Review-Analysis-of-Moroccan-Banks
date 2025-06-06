{% macro get_stop_words() %}
  {{ log("Reading stop words from stop_words.json", info=True) }}

  {% set stop_words_file = load_file('models/stop_words.json') %}
  {% set stop_words_json = fromjson(stop_words_file) %}
  {{ return(stop_words_json.stop_words) }}
{% endmacro %}
    