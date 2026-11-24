# Graph Report - chinese  (2026-11-24)

## Corpus Check
- Corpus is ~21,797 words - fits in a single context window. You may not need a graph.

## Summary
- 85 nodes · 194 edges · 10 communities (7 shown, 3 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9

## God Nodes (most connected - your core abstractions)
1. `draw_box()` - 16 edges
2. `cmd_chat()` - 16 edges
3. `main()` - 12 edges
4. `main()` - 9 edges
5. `load_curriculum()` - 8 edges
6. `cmd_reflex()` - 8 edges
7. `load_progress()` - 7 edges
8. `load_vocab()` - 7 edges
9. `cmd_session_prepare()` - 7 edges
10. `cmd_session_run()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `cmd_session_run()`  [EXTRACTED]
  hoc.py → agy_ui.py

## Import Cycles
- None detected.

## Communities (10 total, 3 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.27
Nodes (12): cmd_list(), cmd_record(), cmd_reflex(), cmd_report(), cmd_study(), load_curriculum(), load_progress(), main() (+4 more)

### Community 1 - "Community 1"
Cohesion: 0.26
Nodes (5): auto_pull(), auto_push(), main(), run_git(), setup_token()

### Community 2 - "Community 2"
Cohesion: 0.25
Nodes (6): cmd_record(), cmd_status(), load_progress(), print_help(), save_progress(), show_suggestions()

### Community 3 - "Community 3"
Cohesion: 0.25
Nodes (7): add_or_update_vocab(), cmd_export_anki(), cmd_list_vocab(), load_vocab(), lookup_word(), query_dict_db(), save_vocab()

### Community 5 - "Community 5"
Cohesion: 0.46
Nodes (8): cmd_add_vocab(), cmd_session_prepare(), cmd_session_run(), cmd_show_drill(), cmd_show_explain(), cmd_show_result(), draw_box(), main()

### Community 6 - "Community 6"
Cohesion: 0.25
Nodes (5): cmd_chat(), cmd_sync(), get_terminal_width(), quick_drill_one(), show_process_profile()

### Community 7 - "Community 7"
Cohesion: 0.67
Nodes (3): interactive_prompt(), clear_menu(), render()

## Knowledge Gaps
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `cmd_session_run()` connect `Community 5` to `Community 1`, `Community 2`, `Community 6`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Why does `interactive_prompt()` connect `Community 7` to `Community 2`, `Community 6`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Why does `cmd_chat()` connect `Community 6` to `Community 2`, `Community 3`, `Community 5`, `Community 7`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._