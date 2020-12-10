import sys
import yaml
from jinja2 import Template

data = yaml.safe_load(sys.stdin)

template = Template("""\
<div class="sponsors-avatars-top">
{%- for entry in data %}
    {%- if entry.tier == "top" %}
    <div class="sponsors-avatar-top">
        <a href="https://github.com/{{entry.username}}">
            <img class="avatar" src="{{entry.avatar}}" title="{{entry.name}}"/>
        </a>
    </div>
    {%- endif %}
{%- endfor %}
</div>

<div class="sponsors-avatars-bottom">
{%- for entry in data %}
    {%- if entry.tier != "top" %}
    <div class="sponsors-avatar-bottom">
        <a href="https://github.com/{{entry.username}}">
            <img class="avatar" src="{{entry.avatar}}" title="{{entry.name}}"/>
        </a>
    </div>
    {%- endif %}
{%- endfor %}
</div>
""")
sys.stdout.write(template.render(data=data))

'''
<div class="sponsors-avatars-top docutils container">
<div class="sponsors-avatar-top docutils container">
<img alt="../img/sponsors/top/601732.png" class="avatar" src="../img/sponsors/top/601732.png" />
</div>
<div class="sponsors-avatar-top docutils container">
<img alt="../img/sponsors/top/37837.png" class="avatar" src="../img/sponsors/top/37837.png" />
</div>
<div class="sponsors-avatar-top docutils container">
<img alt="../img/sponsors/top/3852020.jpeg" class="avatar" src="../img/sponsors/top/3852020.jpeg" />
</div>
<div class="sponsors-avatar-top docutils container">
<img alt="../img/sponsors/top/330373.png" class="avatar" src="../img/sponsors/top/330373.png" />
</div>
</div>
<div class="sponsors-avatars-bottom docutils container">
<div class="sponsors-avatar-bottom docutils container">
<img alt="../img/sponsors/94721.jpeg" class="avatar" src="../img/sponsors/94721.jpeg" />
</div>
<div class="sponsors-avatar-bottom docutils container">
<img alt="../img/sponsors/115712.jpeg" class="avatar" src="../img/sponsors/115712.jpeg" />
</div>
<div class="sponsors-avatar-bottom docutils container">
<img alt="../img/sponsors/174182.png" class="avatar" src="../img/sponsors/174182.png" />
</div>
<div class="sponsors-avatar-bottom docutils container">
<img alt="../img/sponsors/2050405.png" class="avatar" src="../img/sponsors/2050405.png" />
</div>
<div class="sponsors-avatar-bottom docutils container">
<img alt="../img/sponsors/3085224.png" class="avatar" src="../img/sponsors/3085224.png" />
</div>
<div class="sponsors-avatar-bottom docutils container">
<img alt="../img/sponsors/7447491.jpeg" class="avatar" src="../img/sponsors/7447491.jpeg" />
</div>
<div class="sponsors-avatar-bottom docutils container">
<img alt="../img/sponsors/7826876.jpeg" class="avatar" src="../img/sponsors/7826876.jpeg" />
</div>
<div class="sponsors-avatar-bottom docutils container">
<img alt="../img/sponsors/14254614.png" class="avatar" src="../img/sponsors/14254614.png" />
</div>
<div class="sponsors-avatar-bottom docutils container">
<img alt="../img/sponsors/16618300.jpeg" class="avatar" src="../img/sponsors/16618300.jpeg" />
</div>
</div>
</div>
'''
