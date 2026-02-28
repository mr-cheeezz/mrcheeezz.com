{% for page in nav_href %}
  document.getElementsByClassName('{{ page.name }}__href').onclick = function() {
    window.location.href = `https://{{ url }}{% if not page.link %}{% else %}/{{ page.link }}{% endif %}`;
    return false;
  }
{% endfor %}