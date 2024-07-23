from urllib.request import urlopen

data = urlopen('https://www.barbercosmo.ca.gov/laws_regs/act_regs_vt.pdf').read()
print(data)