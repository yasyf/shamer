<!--
This is a sample _comment.md template that we use at Localytics. You should customize this for your use case.
-->

{% if (args.ruby|float - storage.get('master').ruby[0]|float < -0.1) or (args.js|float - storage.get('master').js[0]|float < -0.1) %}
![Feel Bad](http://i.imgur.com/oXW25lP.jpg)
{% endif %}

## Code Coverage

**Reports have been generated for this branch: <a href="{{ url }}?{{ pr.title|urlencode }}" target="_blank">{{ pr.head.ref }}</a>**

{% if args.ruby %}
### Ruby/Rails: ![Ruby/Rails](https://s3.amazonaws.com/assets.coveralls.io/badges/coveralls_{{ args.ruby|int }}.png)
Current coverage for `{{ pr.head.ref }}` is at **{{ args.ruby }}**%
**{{ args.ruby|float - storage.get('master').ruby[0]|float }}**% change from `master`
{% endif %}

{% if args.js %}
### JavaScript: ![JavaScript](https://s3.amazonaws.com/assets.coveralls.io/badges/coveralls_{{ args.js|int }}.png)
Current coverage for `{{ pr.head.ref }}` is at **{{ args.js }}**%
**{{ args.js|float - storage.get('master').js[0]|float }}**% change from `master`
{% endif %}

{% if rank %}
Your rank on the [Localytics Coverage Leaderboard]({{ url_for('leaderboard_view', _external=True) }}) is **{{ rank[0] }}** out of **{{ rank[1] }}**!
{% endif %}
