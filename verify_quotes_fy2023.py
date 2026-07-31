import io, re

p = 'data/raw/nvda_fy2023_10k.html'
with io.open(p, encoding='utf-8', errors='replace') as f:
    raw = f.read()

def detag(s):
    s = re.sub(r'<[^>]+>', '', s)
    s = s.replace('&nbsp;', ' ').replace('&#160;', ' ').replace('&amp;', '&')
    s = re.sub(r'[ \t]+', ' ', s)
    return s

full = detag(raw)
full_norm = re.sub(r'\s+', ' ', full)

tests = {
 'SIG001a': 'In February 2023, we completed an assessment of the useful lives of our property, plant, and equipment. Based on advances in technology and usage rate, we increased the estimated useful life of a majority of the server, storage, and network equipment from three years to a range of four to five years, and assembly and test equipment from five years to seven years.',
 'SIG001b': 'This change in accounting estimate became effective at the beginning of fiscal year 2024. Based on the carrying amounts of a majority of our server, storage, network, and assembly and test equipment, net in use as of the end of fiscal year 2023, it is estimated this change will increase our fiscal year 2024 operating income by $133 million as a result of the reduction in depreciation expense.',
 'SIG002a': 'Property and equipment are stated at cost. Depreciation of property and equipment is computed using the straight-line method based on the estimated useful lives of the assets, generally three to five years.',
 'SIG002b': 'The estimated useful lives of our buildings are up to thirty years.',
 'SIG002c': 'Leasehold improvements and assets recorded under finance leases are amortized over the shorter of the expected lease term or the estimated useful life of the asset.',
 'SIG004': 'Long-lived assets, such as property and equipment and intangible assets subject to amortization, are reviewed for impairment whenever events or changes in circumstances indicate that the carrying amount of an asset or asset group may not be recoverable.',
 'SIG005a': 'At the end of fiscal year 2023, purchase obligations and prepaid supply agreements represented more than half of our total supply.',
 'SIG005b': 'We may incur inventory provisions if our inventory or supply commitments are misaligned with demand for our products.',
 'SIG006': 'We have also written-down our inventory, incurred cancellation penalties, and recorded impairments. These impacts were amplified by our placement of non-cancellable and non-returnable purchasing terms, well in advance of our historical lead times',
 'SIG007': 'Situations that may result in excess or obsolete inventory or excess product purchase commitments include changes in business and economic conditions, changes in market conditions, sudden and significant decreases in demand for our products, inventory obsolescence because of changing technology and customer requirements, new product introductions resulting in less demand for existing products',
 'SIG008a': '$2.17 billion of inventory provisions in fiscal year 2023, which consists of approximately $1.04 billion for inventory on hand and approximately $1.13 billion for inventory purchase obligations in excess of our current demand projections.',
 'SIG008b': 'Inventory provisions totaled $2.17 billion and $354 million for fiscal years 2023 and 2022, respectively.',
 'SIG008c': 'the overall net effect on our gross margin was an unfavorable impact of 7.5% and 0.9% in fiscal years 2023 and 2022, respectively.',
 'SIG008d': 'Inventory provisions for excess inventory and purchase obligations totaled $2.17 billion in fiscal year 2023.',
 'SIG009a': 'We are currently transitioning the architecture of our Data Center, Professional Visualization, and Gaming products.',
 'SIG009b': 'We have experienced and may in the future experience reduced demand for current generation architectures when customers anticipate transitions',
 'SIG010': 'Depreciation expense for fiscal years 2023, 2022, and 2021 was $844 million, $611 million, and $486 million, respectively.',
 'SIG011': 'We recorded an acquisition termination cost related to the Arm transaction of $1.35 billion in fiscal year 2023 reflecting the write-off of the prepayment provided at signing.',
 'SIG012a': 'CMP revenue was nominal in fiscal year 2023 and $550 million in fiscal year 2022.',
 'SIG012b': 'driven by $2.17 billion of inventory charges largely relating to excess supply of NVIDIA Ampere architecture Gaming and Data Center products',
 'GOODWILL': 'we completed our annual qualitative impairment tests and concluded that goodwill was not impaired in any of these years.',
 'SIG009c': 'Product transitions are complex and frequently negatively impact our revenue as we often ship both new and legacy architecture products simultaneously',
}

fails = 0
for k, v in tests.items():
    vn = re.sub(r'\s+', ' ', v)
    ok = vn in full_norm
    print(k, 'OK' if ok else 'MISS')
    if not ok:
        fails += 1
        # show closest context
        key = vn[:40]
        i = full_norm.find(key)
        print('   ctx:', full_norm[max(0,i-50):i+250] if i >= 0 else 'KEY NOT FOUND')
print('FAILS:', fails)
