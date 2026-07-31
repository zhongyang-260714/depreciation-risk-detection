p = r"D:\depreciation-risk-detection\scripts\fix_oracle_nvidia_v4.py"
s = open(p, encoding="utf-8").read()
old = '（"5→8"安错对象）'
new = '（' + chr(0x201C) + '5→8' + chr(0x201D) + '安错对象）'
assert old in s, "old substring not found in script"
s = s.replace(old, new)
open(p, "w", encoding="utf-8").write(s)
print("patched L237 old-string quotes -> full-width")
