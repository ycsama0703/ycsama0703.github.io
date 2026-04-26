---
layout: home
---

{% if site.data.publications and site.data.publications.size > 0 %}
<section class="auto-pubs">
<h2>Publications <small>(auto-synced from OpenReview)</small></h2>
<ul>
{% for p in site.data.publications %}
  <li>
    <strong>{{ p.title }}</strong><br/>
    {% for a in p.authors %}{% if a == site.author %}<em>{{ a }}</em>{% else %}{{ a }}{% endif %}{% unless forloop.last %}, {% endunless %}{% endfor %}<br/>
    <small>
      {% if p.venue %}{{ p.venue }}{% endif %}{% if p.year %}, {{ p.year }}{% endif %}
      {% if p.openreview %} · <a href="{{ p.openreview }}">OpenReview</a>{% endif %}
      {% if p.pdf %} · <a href="{{ p.pdf }}">PDF</a>{% endif %}
    </small>
  </li>
{% endfor %}
</ul>
</section>
{% endif %}
