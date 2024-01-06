### stringモジュールのTemplateクラススニペット ###
### 出力をカスタマイズする際に使用 ###

from string import Template

# 以下template.txtの内容
# food: $food
# drink: $drink


with open('template.txt') as f:
  t = Template(f.read())

contents = t.substitute(food='apple', drink='coffee')
print(contents)
# food: apple
# drink: coffee
