{#
  Cleaning helpers for the silver layer. Bronze stores everything as TEXT.
#}

{# text -> numeric. Accepts '501.0', '-3', and a few number words seen in the data. #}
{% macro clean_number(col) %}
    case
        when trim({{ col }}) ~ '^-?[0-9]+(\.[0-9]+)?$' then trim({{ col }})::numeric
        when lower(trim({{ col }})) = 'two hundred'    then 200
        when lower(trim({{ col }})) = 'fifteen'        then 15
        else null
    end
{% endmacro %}

{# text -> date. Accepts YYYY-MM-DD and DD-MM-YYYY, anything else becomes NULL. #}
{% macro clean_date(col) %}
    case
        when trim({{ col }}) ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' then to_date(trim({{ col }}), 'YYYY-MM-DD')
        when trim({{ col }}) ~ '^[0-9]{2}-[0-9]{2}-[0-9]{4}$' then to_date(trim({{ col }}), 'DD-MM-YYYY')
        else null
    end
{% endmacro %}
