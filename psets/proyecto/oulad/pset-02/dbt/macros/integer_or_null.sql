{% macro integer_or_null(column) -%}
case when regexp_like(trim({{ column }}), '^[-+]?[0-9]+$')
     then try_to_number(trim({{ column }}), 38, 0) end
{%- endmacro %}

{% macro invalid_integer(column) -%}
(nullif(trim({{ column }}), '') is not null and {{ integer_or_null(column) }} is null)
{%- endmacro %}
