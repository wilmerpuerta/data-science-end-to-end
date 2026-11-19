{% macro generate_schema_name(custom_schema_name, node) -%}
  {%- set chosen = (custom_schema_name or target.schema) | trim | upper -%}
  {%- if node.resource_type == 'test' -%}
    {%- set chosen = target.schema | trim | upper -%}
  {%- endif -%}
  {%- if chosen not in ['BRONZE', 'SILVER', 'GOLD', 'ANALYTICS'] -%}
    {{ exceptions.raise_compiler_error('Esquema fuera del contrato PSet2') }}
  {%- endif -%}
  {{ chosen }}
{%- endmacro %}
