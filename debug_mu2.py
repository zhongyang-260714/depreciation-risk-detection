import sys
for key in list(sys.modules.keys()):
    if 'scorer_calculator' in key or 'ai_annotation' in key:
        del sys.modules[key]

sys.path.insert(0, 'src')
from ai_annotation.scorer_calculator import _extract_life_years_from_context

text = """Property,
 plant, and equipment is stated at cost and depreciated using the 
straight-line method over estimated useful lives of generally 10 to 30 years for buildings, 7 years for production equipment, up to 7 years for other equipment, and 3 to 5 years for software. Assets held for sale are carried at the lower of 
estimated fair value or carrying value and are included in current 
assets."""

result = _extract_life_years_from_context(text)
print(f"Result: {result}")
