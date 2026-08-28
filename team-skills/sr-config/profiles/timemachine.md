# TimeMachine 配置 Profile

本 profile 只描述 TimeMachine 项目的五行表头、`INDEX` 和配置模式。通用流程与 schema 由 `SKILL.md`、`references/rules_and_schema.md` 和 `references/change_set.md` 定义。

## 本机目录

优先读取同目录的 `timemachine.local.yaml`。文件存在且 `config_root` 有效时直接采用并写入 change set；缺失、失效或目录中没有 `.xlsx/.xlsm` 时询问用户，确认后更新该文件。绝对路径只保存在本机配置，不写入本 profile。

配置目录扫描排除名称包含 `.backup.`、`.tmp.`、`.failed.` 的工作簿。

## 模式状态

- `verified`：来源元数据齐全，且当前 `config_root` 下来源文件的 SHA-256 与记录一致；可以作为候选 schema 的已验证证据。
- `candidate`：模式本身缺少稳定来源，或已验证模式的文件缺失、哈希失配、目标字段契约不同；必须进入确认门。

状态不能静默升级。`verified` 来源失配时降级为 `candidate` 并记录 `profile_conflict`。每个来源记录的 `source_root` 都指向逻辑键 `config_root`。

## 已验证模式

### `scalar_enum`

单值整数枚举。枚举含义只在目标字段和来源一致时复用，不跨字段套用。

```yaml
sources:
  - source_root: config_root
    workbook: A009-领袖表.xlsx
    sheet: 英雄基础表
    field_or_cell: quality,type
    verified_at: '2026-08-27'
    file_hash: sha256:84a53c1173cb58a1bcc19c3f261a472cd05d38887a258ced905d9548f0504d0c
  - source_root: config_root
    workbook: B009-领袖装备表.xlsx
    sheet: 装备基础表
    field_or_cell: rank,pos
    verified_at: '2026-08-27'
    file_hash: sha256:1a3e512109b5de6d09f2cb8488c140622d6d32fe717521bee59de08077e2ee7c
```

已知枚举：品质/装备品阶 `1=灰,2=绿,3=蓝,4=紫,5=橙,6=红`；英雄兵种 `1=步兵,2=骑兵,3=弓兵`；装备槽位 `1=头,2=甲,3=手,4=脚`。

### `id_reference`

单 ID 外键。契约必须声明目标工作簿、工作表、键字段和空值策略。

```yaml
sources:
  - source_root: config_root
    workbook: A009-领袖表.xlsx
    sheet: 英雄基础表
    field_or_cell: piecesGid
    verified_at: '2026-08-27'
    file_hash: sha256:84a53c1173cb58a1bcc19c3f261a472cd05d38887a258ced905d9548f0504d0c
```

### `id_level_count`

单组格式为 `gid,level,count`；多组分隔符和尾分号只有在目标字段证据确认后启用。

```yaml
sources:
  - source_root: config_root
    workbook: B009-领袖装备表.xlsx
    sheet: 装备精炼表
    field_or_cell: upgradeCost
    verified_at: '2026-08-27'
    file_hash: sha256:1a3e512109b5de6d09f2cb8488c140622d6d32fe717521bee59de08077e2ee7c
```

### `typed_value`

格式为 `attribute_gid,value;`，组内逗号、组间分号。尾分号和数值边界以目标字段批注为准。军团属性与冒险属性是否成对新增属于契约选择，未确认时形成 blocker。

```yaml
sources:
  - source_root: config_root
    workbook: B009-领袖装备表.xlsx
    sheet: 装备强化表
    field_or_cell: effect,xGameAttr
    verified_at: '2026-08-27'
    file_hash: sha256:1a3e512109b5de6d09f2cb8488c140622d6d32fe717521bee59de08077e2ee7c
  - source_root: config_root
    workbook: A009-领袖表.xlsx
    sheet: 英雄基础表
    field_or_cell: effectStarMax,xgameAttrStarMax
    verified_at: '2026-08-27'
    file_hash: sha256:84a53c1173cb58a1bcc19c3f261a472cd05d38887a258ced905d9548f0504d0c
  - source_root: config_root
    workbook: B010-副玩法属性表.xlsx
    sheet: 领袖属性表
    field_or_cell: id
    verified_at: '2026-08-27'
    file_hash: sha256:b8cbdc9ea3ff81713c50b5ceed855e5d7ee34cc9e31146aad36146c6052a5039
```

### `weight_scalar`

单字段整数权重，不是百分比，不包含条目 ID。总和规则读取目标表契约。

```yaml
sources:
  - source_root: config_root
    workbook: A009-领袖表.xlsx
    sheet: 英雄招募表
    field_or_cell: baseweight,upWeight,guaranteeWeight
    verified_at: '2026-08-27'
    file_hash: sha256:84a53c1173cb58a1bcc19c3f261a472cd05d38887a258ced905d9548f0504d0c
```

### `ratio_scaled`

整数缩放比例；只有目标字段证据一致时才采用 `10000=100%`。

```yaml
sources:
  - source_root: config_root
    workbook: A009-领袖表.xlsx
    sheet: 英雄升星表
    field_or_cell: effectRate,xgameAttrRate,powerRate
    verified_at: '2026-08-27'
    file_hash: sha256:84a53c1173cb58a1bcc19c3f261a472cd05d38887a258ced905d9548f0504d0c
```

### `growth_curve`

以 `starType + star` 为复合键的成长曲线。

```yaml
sources:
  - source_root: config_root
    workbook: A009-领袖表.xlsx
    sheet: 英雄升星表
    field_or_cell: starType,star,cost,effectRate,xgameAttrRate,powerRate
    verified_at: '2026-08-27'
    file_hash: sha256:84a53c1173cb58a1bcc19c3f261a472cd05d38887a258ced905d9548f0504d0c
```

### `condition_selector`

格式为 `type,param1,param2,param3;`，第一段决定后续参数语义。

```yaml
sources:
  - source_root: config_root
    workbook: A028-功能开启表.xlsx
    sheet: 功能开启
    field_or_cell: section1
    verified_at: '2026-08-27'
    file_hash: sha256:728a644d372ef101862f202771e267f20a9a61c8db592e695dcae51de581173d
```

### `key_value`

`key` 是唯一字符串键；`value` 的 codec 按目标 key 的说明解析。

```yaml
sources:
  - source_root: config_root
    workbook: A012-全局变量表.xlsx
    sheet: 全局变量表
    field_or_cell: key,value
    verified_at: '2026-08-27'
    file_hash: sha256:c1e732a6713ca987b16fc06fa466b7b19e7be1c8216549212fac93c858d2f285
```

### `skill_row`

技能行包含 `gid,skill_slot,level,unlock,power,skill,descRule,skillType,effectParam,effects,xgameAttr`。字段大小写保持来源原样。

```yaml
sources:
  - source_root: config_root
    workbook: A009-领袖表.xlsx
    sheet: 英雄技能表
    field_or_cell: gid,skill_slot,level,unlock,power,skill,descRule,skillType,effectParam,effects,xgameAttr
    verified_at: '2026-08-27'
    file_hash: sha256:84a53c1173cb58a1bcc19c3f261a472cd05d38887a258ced905d9548f0504d0c
```

### `id_list`

逗号分隔的有序 ID 列表；ID 来源和最大数量读取目标字段批注。

```yaml
sources:
  - source_root: config_root
    workbook: A009-领袖表.xlsx
    sheet: 英雄基础表
    field_or_cell: heroPos
    verified_at: '2026-08-27'
    file_hash: sha256:84a53c1173cb58a1bcc19c3f261a472cd05d38887a258ced905d9548f0504d0c
```

## 候选模式

### `weighted_pair`

候选格式为 `entry_gid,weight`。当前已验证字段只能证明 `weight_scalar`，不能证明二元组。

```yaml
sources:
  - source_root: config_root
    workbook: null
    sheet: null
    field_or_cell: null
    verified_at: null
    file_hash: null
confirmation_required: [真实单元格样例, ID引用来源, 分隔符规则]
```

### `prob_display`

候选格式为 `item_gid,count,probability;`，只表达展示概率，不替代实际抽取权重。

```yaml
sources:
  - source_root: config_root
    workbook: null
    sheet: null
    field_or_cell: null
    verified_at: null
    file_hash: null
confirmation_required: [目标字段批注, 概率单位, 展示项对应规则]
```

### `text_key`

候选约定为 `n{gid}`、`d{gid}`、`d{skill}`。当前缺少可定位的工作簿来源，只能在目标规则确认后采用。

```yaml
sources:
  - source_root: config_root
    workbook: null
    sheet: null
    field_or_cell: null
    verified_at: null
    file_hash: null
confirmation_required: [正式规则来源, 目标字段或文本表定位]
```
