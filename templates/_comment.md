<!--
This is a sample _comment.md template that we use at Localytics. You should customize this for your use case.
-->

{% if diffs.values()|min < -0.1 %}
![Feel Bad](http://i.imgur.com/oXW25lP.jpg)
(Not right? Try merging master into your branch!)
{% endif %}

## Code Coverage

**Reports have been generated for this branch: <a href="{{ url }}?{{ pr.title|urlencode }}" target="_blank">{{ pr.head.ref }}</a>**

{% for lang, diff in diffs.items() %}

### {{ lang|lang_nice }}: ![{{ lang|lang_nice }}](http://img.shields.io/badge/LocCoverage-{{ args[lang]|int }}%25-{{ 'red' if diff < 0 else 'brightgreen' }}.svg?style=flat)
Current coverage for `{{ pr.head.ref }}` is at **{{ args[lang] }}**%
**{{ diff }}**% change from <a href='https://github.com/{{ pr.head.repo.organization.login }}/{{ pr.head.repo.name }}/tree/{{ base }}'>`master`</a> at {{ base }}


{% endfor %}

{% if rank %}
Your rank on the [Localytics Coverage Leaderboard]({{ url_for('leaderboard_view', _external=True) }}) for `{{ pr.head.repo.name }}` is **{{ rank[0] }}** out of **{{ rank[1] }}**!
{% endif %}
