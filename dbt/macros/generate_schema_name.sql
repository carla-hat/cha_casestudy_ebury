{#
  By default dbt builds the schema as <target schema>_<custom schema>
  (e.g. public_silver). This override uses the custom schema as-is (silver).
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {{ custom_schema_name | trim if custom_schema_name is not none else target.schema }}
{%- endmacro %}
