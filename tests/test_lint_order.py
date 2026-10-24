import copy, importlib.util, json, unittest
from pathlib import Path

P = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location('lint_order', P / 'scripts' / 'lint_order.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

BASE = json.loads((P / 'assets' / 'demo-input.json').read_text(encoding='utf-8'))
BASE['menu']['products'][0].setdefault('groups', [])

def run(mut=None):
    d = copy.deepcopy(BASE)
    if mut: mut(d)
    return mod.lint(d)

class LintTests(unittest.TestCase):
    def test_pass_supported(self): self.assertEqual(run()['summary'], '当前检查范围通过')
    def test_empty_menu_unknown(self):
        r = run(lambda d: d['menu'].update(products=[])); self.assertEqual(r['summary'], '待确认')
    def test_ambiguous_alias(self):
        def m(d):
            d['order'][0].pop('product_id')
            d['order'][0]['name'] = '汉堡别名'
            d['menu']['products'].append({'id':'x','name':'另品','aliases':['汉堡别名']})
        r=run(m); self.assertTrue(any(x['code']=='identity' and x['state']=='unknown' for x in r['findings']))
    def test_ambiguous_target(self):
        r=run(lambda d: d['order'][0]['modifiers'].__setitem__(0, {'name':'去洋葱','target':'missing'})); self.assertIn('待确认', r['summary'])
    def test_unknown_modifier(self):
        r=run(lambda d: d['order'][0]['modifiers'].__setitem__(0, {'name':'加未知酱','target':'self'})); self.assertTrue(any(x['state']=='unknown' for x in r['findings']))
    def test_unsupported_modifier(self):
        def m(d): d['menu']['products'][0]['modifiers']['去洋葱']='unsupported'
        self.assertEqual(run(m)['summary'], '需修正')
    def test_missing_modifier_field_unknown(self):
        def m(d): d['menu']['products'][0].pop('modifiers'); d['order'][0]['modifiers']=[{'name':'去洋葱','target':'self'}]
        self.assertEqual(run(m)['summary'], '待确认')
    def test_quantity_bool(self): self.assertEqual(run(lambda d: d['order'][0].update(quantity=True))['summary'], '需修正')
    def test_quantity_negative(self): self.assertEqual(run(lambda d: d['order'][0].update(quantity=-1))['summary'], '需修正')
    def test_quantity_decimal(self): self.assertEqual(run(lambda d: d['order'][0].update(quantity=1.5))['summary'], '需修正')
    def test_quantity_missing(self): self.assertEqual(run(lambda d: d['order'][0].pop('quantity'))['summary'], '待确认')
    def test_group_incomplete(self):
        def m(d):
            p=d['menu']['products'][0]; p['groups']=[{'id':'drink','min':1,'max':1,'allowed_ids':['tea']}]; p['evidence']['groups']={'store_id':'store-demo','queried_at':'2026-10-24T09:55:00+08:00','source':'query-meal-detail','path':'groups','excerpt':'drink','response_ref':'demo-2'}
        self.assertEqual(run(m)['summary'], '需修正')
    def test_store_mismatch_unknown(self):
        def m(d): d['menu']['products'][0]['evidence']['identity']['store_id']='other'
        self.assertIn(run(m)['summary'], ('待确认','需修正'))
    def test_time_missing_schema(self):
        d=copy.deepcopy(BASE); d.pop('checked_at')
        with self.assertRaises(mod.SchemaError): mod.lint(d)
    def test_schema_error_unknown_top(self):
        d=copy.deepcopy(BASE); d['oops']=1
        with self.assertRaises(mod.SchemaError): mod.lint(d)
    def test_invalid_product_schema(self):
        d=copy.deepcopy(BASE); d['menu']['products'][0]['id']=1
        with self.assertRaises(mod.SchemaError): mod.lint(d)
    def test_unit_mismatch(self): self.assertEqual(run(lambda d: d['order'][0].update(unit='盒'))['summary'], '需修正')
    def test_output_json_serializable(self): json.dumps(run(), ensure_ascii=False)

if __name__ == '__main__': unittest.main()
