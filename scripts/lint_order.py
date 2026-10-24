#!/usr/bin/env python3
"""麦麦点餐质检：仅处理适配器输入，不联网、不交易。"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


class SchemaError(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise SchemaError(message)


def obj(value, allowed, required=()):
    require(isinstance(value, dict), '应为对象')
    require(not (set(value) - set(allowed)), '存在未知字段：' + str(set(value) - set(allowed)))
    require(set(required) <= set(value), '缺少必需字段：' + str(set(required) - set(value)))


def text(value):
    require(isinstance(value, str) and bool(value.strip()), '应为非空字符串')


def texts(value):
    require(isinstance(value, list), '应为字符串列表')
    for x in value:
        text(x)
    require(len(value) == len(set(value)), '列表值重复')


def timestamp(value):
    text(value)
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        require(dt.tzinfo is not None, '时间必须带时区')
        return dt
    except ValueError as exc:
        raise SchemaError('无效的 ISO 8601 时间') from exc


def unique(items, key):
    require(len(items) == len({x[key] for x in items}), key + ' 重复')


def validate(data):
    obj(data, ['schema_version', 'store_id', 'checked_at', 'menu', 'order'], ['schema_version', 'store_id', 'checked_at', 'menu', 'order'])
    require(data['schema_version'] == '1.0', '不支持的 schema_version')
    text(data['store_id'])
    timestamp(data['checked_at'])
    menu = data['menu']
    obj(menu, ['products'], ['products'])
    require(isinstance(menu['products'], list), 'products 应为列表')
    for p in menu['products']:
        obj(p, ['id', 'name', 'aliases', 'units', 'groups', 'modifiers', 'evidence'], ['id', 'name'])
        text(p['id']); text(p['name'])
        for k in ['aliases', 'units']:
            if k in p:
                texts(p[k])
        if 'groups' in p:
            require(isinstance(p['groups'], list), 'groups 应为列表')
            for g in p['groups']:
                obj(g, ['id', 'min', 'max', 'allowed_ids'], ['id', 'min', 'max', 'allowed_ids'])
                text(g['id']); texts(g['allowed_ids'])
                require(type(g['min']) is int and type(g['max']) is int and 0 <= g['min'] <= g['max'], '套餐组数量边界无效')
            unique(p['groups'], 'id')
        if 'modifiers' in p:
            require(isinstance(p['modifiers'], dict), 'modifiers 应为对象')
            for k, v in p['modifiers'].items():
                text(k)
                require(v in ('supported', 'unsupported', 'unknown'), 'modifier 状态无效')
        if 'evidence' in p:
            obj(p['evidence'], ['identity', 'aliases', 'units', 'groups', 'modifiers'])
            for e in p['evidence'].values():
                obj(e, ['store_id', 'queried_at', 'source', 'path', 'excerpt', 'response_ref'])
                for k, v in e.items():
                    if k == 'queried_at':
                        timestamp(v)
                    else:
                        text(v)
    unique(menu['products'], 'id')
    require(isinstance(data['order'], list) and bool(data['order']), 'order 应为非空列表')
    for line in data['order']:
        obj(line, ['line_id', 'product_id', 'name', 'quantity', 'unit', 'selections', 'modifiers'], ['line_id'])
        text(line['line_id'])
        for k in ['product_id', 'name', 'unit']:
            if k in line:
                text(line[k])
        if 'quantity' in line:
            require(type(line['quantity']) in (int, float, bool, str) or line['quantity'] is None, 'quantity 类型无效')
        selections = line.get('selections', [])
        require(isinstance(selections, list), 'selections 应为列表')
        for s in selections:
            obj(s, ['selection_id', 'group_id', 'product_id'], ['selection_id', 'group_id', 'product_id'])
            for v in s.values():
                text(v)
        unique(selections, 'selection_id')
        require(isinstance(line.get('modifiers', []), list), 'modifiers 应为列表')
        for m in line.get('modifiers', []):
            obj(m, ['name', 'target'], ['name'])
            text(m['name'])
            if 'target' in m:
                text(m['target'])
    unique(data['order'], 'line_id')


def lint(data):
    validate(data)
    findings = []
    now = timestamp(data['checked_at'])
    products = data['menu']['products']
    by_id = {p['id']: p for p in products}

    def emit(code, state, message, line, evidence=None):
        findings.append({'code': code, 'state': state, 'severity': {'pass': 'info', 'fail': 'error', 'unknown': 'warning'}[state], 'line_id': line, 'message': message, 'evidence': evidence or []})

    def usable(p, field):
        e = p.get('evidence', {}).get(field, {})
        needed = {'store_id', 'queried_at', 'source', 'path', 'excerpt', 'response_ref'}
        if not needed <= set(e):
            return False, [e] if e else []
        age = (now - timestamp(e['queried_at'])).total_seconds()
        return e['store_id'] == data['store_id'] and 0 <= age <= 1800, [e]

    def check(p, field, condition, code, good, bad, line):
        valid, ev = usable(p, field)
        emit(code, ('pass' if condition else 'fail') if valid else 'unknown', (good if condition else bad) if valid else '证据缺失、门店不一致或时间不适用，待确认', line, ev)

    for line in data['order']:
        lid = line['line_id']
        q = line.get('quantity')
        emit('quantity', 'unknown' if 'quantity' not in line else ('pass' if type(q) is int and q > 0 else 'fail'), '数量须为正整数（布尔值无效）', lid)
        pid = line.get('product_id')
        name = line.get('name')
        candidates = [p for p in products if name and (name == p['name'] or name in p.get('aliases', []))]
        p = by_id.get(pid) if pid else (candidates[0] if len(candidates) == 1 else None)
        if p is None:
            emit('identity', 'unknown', '名称/ID 无匹配或别名有歧义；不代表下架', lid)
            emit('unit', 'unknown', '餐品未确定，单位待确认', lid)
            emit('groups', 'unknown', '餐品未确定，套餐结构待确认', lid)
            for _ in line.get('modifiers', []):
                emit('modifier', 'unknown', '餐品未确定，修饰目标与支持情况待确认', lid)
            continue
        matches = not name or name == p['name'] or name in p.get('aliases', [])
        alias_ok = not name or name == p['name'] or usable(p, 'aliases')[0]
        if not alias_ok:
            emit('identity', 'unknown', '别名映射缺少适用证据', lid)
        else:
            check(p, 'identity', matches, 'identity', '名称与餐品 ID 对应', '名称与餐品 ID 不匹配', lid)
        if 'unit' not in line or 'units' not in p:
            emit('unit', 'unknown', '数量单位未明确或无单位证据', lid)
        else:
            check(p, 'units', line['unit'] in p['units'], 'unit', '数量单位匹配', '数量单位不匹配', lid)
        sels = line.get('selections', [])
        if 'groups' not in p:
            emit('groups', 'unknown', '套餐必选组信息缺失，不推断无必选项', lid)
        else:
            groups = p['groups']
            gids = {g['id'] for g in groups}
            good = all(s['group_id'] in gids for s in sels)
            for g in groups:
                selected = [s for s in sels if s['group_id'] == g['id']]
                good = good and g['min'] <= len(selected) <= g['max'] and all(s['product_id'] in g['allowed_ids'] for s in selected)
            check(p, 'groups', good, 'groups', '套餐组选择数量与允许 ID 符合', '套餐组不全、数量越界或含非允许 ID', lid)
        targets = {'self': p}
        targets.update({s['selection_id']: by_id.get(s['product_id']) for s in sels})
        for m in line.get('modifiers', []):
            target = m.get('target')
            if target is None or target not in targets or targets[target] is None:
                emit('modifier', 'unknown', '修饰目标缺失、有歧义或未解析，不能擅自归属', lid)
                continue
            tp = targets[target]
            valid, ev = usable(tp, 'modifiers')
            identity_valid, _ = usable(tp, 'identity')
            groups_valid = target == 'self' or ('groups' in p and usable(p, 'groups')[0] and any(s['selection_id'] == target and any(g['id'] == s['group_id'] and s['product_id'] in g['allowed_ids'] for g in p['groups']) for s in sels))
            state = tp.get('modifiers', {}).get(m['name'], 'unknown') if valid and identity_valid and groups_valid else 'unknown'
            result = {'supported': 'pass', 'unsupported': 'fail', 'unknown': 'unknown'}[state]
            emit('modifier', result, m['name'] + '：' + {'supported': '明确支持', 'unsupported': '明确不支持', 'unknown': '支持情况未知'}[state], lid, ev)
    states = {f['state'] for f in findings}
    summary = '需修正' if 'fail' in states else ('待确认' if 'unknown' in states else '当前检查范围通过')
    return {'schema_version': '1.0', 'summary': summary, 'store_id': data['store_id'], 'checked_at': data['checked_at'], 'findings': findings, 'limitations': '仅核对当前结构化输入；证据未获独立真实性认证，30分钟时效仅为本地检查策略，不保证菜单仍有效。不承诺食品安全、过敏原或过敏交叉接触安全。'}


def markdown(report):
    labels = {'pass': '通过', 'fail': '不通过', 'unknown': '未知'}
    rows = ['# 麦麦点餐质检', '', '总评：' + report['summary'], '门店：' + report['store_id'], '检查时间：' + report['checked_at'], '']
    for f in report['findings']:
        rows.append('- [' + labels[f['state']] + ' / ' + f['severity'] + '] ' + f['line_id'] + ' · ' + f['code'] + '：' + f['message'])
        for e in f['evidence']:
            rows.append('  - 证据：' + json.dumps(e, ensure_ascii=False, sort_keys=True))
    rows.extend(['', report['limitations']])
    return '\n'.join(rows) + '\n'


def main():
    parser = argparse.ArgumentParser(description='核验结构化点餐草稿；不联网、不交易')
    parser.add_argument('input', help='JSON 文件路径或 -（标准输入）')
    parser.add_argument('--format', choices=['json', 'markdown'], default='markdown')
    args = parser.parse_args()
    try:
        raw = sys.stdin.read() if args.input == '-' else Path(args.input).read_text(encoding='utf-8-sig')
        def pairs(items):
            result = {}
            for key, value in items:
                require(key not in result, 'JSON 键重复：' + key)
                result[key] = value
            return result
        data = json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda s: (_ for _ in ()).throw(SchemaError('非标准 JSON 数值：' + s)))
        report = lint(data)
        print(json.dumps(report, ensure_ascii=False, indent=2) if args.format == 'json' else markdown(report), end='\n' if args.format == 'json' else '')
        return 0
    except (SchemaError, OSError, json.JSONDecodeError, UnicodeError) as exc:
        print(json.dumps({'error': '输入 schema 无效或无法读取', 'detail': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
