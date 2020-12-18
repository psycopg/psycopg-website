import sys
import yaml
from jinja2 import Template

data = yaml.safe_load(sys.stdin)

for entry in data:
    if not entry.get("website"):
        entry["website"] = f"https://github.com/{entry['username']}"

template = Template("""\
<div class="sponsors-avatars sponsors-avatars-top">
{%- for entry in data %}
    {%- if entry.tier == "top" %}
    <div class="sponsors-avatar">
        <a href="{{entry.website}}">
            <img class="avatar" src="{{entry.avatar}}" title="{{entry.name}}"/>
            <div class="sponsor-name">{{entry.name}}</div>
        </a>
    </div>
    {%- endif %}
{%- endfor %}
</div>

<div class="sponsors-avatars sponsors-avatars-mid">
{%- for entry in data %}
    {%- if entry.tier == "mid" %}
    <div class="sponsors-avatar">
        <a href="{{entry.website}}">
            <img class="avatar" src="{{entry.avatar}}" title="{{entry.name}}"/>
            <div class="sponsor-name">{{entry.name}}</div>
        </a>
    </div>
    {%- endif %}
{%- endfor %}
</div>

<div class="sponsors-avatars sponsors-avatars-bottom">
{%- for entry in data %}
    {%- if not entry.tier %}
    <div class="sponsors-avatar">
        <a href="{{entry.website}}">
            <img class="avatar" src="{{entry.avatar}}" title="{{entry.name}}"/>
        </a>
    </div>
    {%- endif %}
{%- endfor %}
</div>
""")

sys.stdout.write(template.render(data=data))
