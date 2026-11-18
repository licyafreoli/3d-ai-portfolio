# AfterQuery Portfolio Scene Projects

Five editable Blender 5.2.4 LTS scene prototypes, created programmatically at the candidate's request. The files and renders are suitable for review and hands-on revision. They are not evidence of independent Blender skill until the candidate understands, revises, and accurately describes their own contributions.

All renders used Cycles on CPU at 900 × 675, 20 samples, with denoising enabled. Render times are single local runs and are not cross-machine benchmarks.

| Project | Scene file | Render | Evaluated triangles | Local render time |
|---|---|---|---:|---:|
| Portable Audio Recorder | `01_portable_audio_recorder/portable_audio_recorder.blend` | `01_portable_audio_recorder/beauty.png` | 11,214 | 29.76 s |
| Modular Sci-Fi Utility Panel | `02_modular_utility_panel/modular_utility_panel.blend` | `02_modular_utility_panel/beauty.png` | 16,606 | 46.33 s |
| Stylized Desk Plant | `03_stylized_desk_plant/stylized_desk_plant.blend` | `03_stylized_desk_plant/beauty.png` | 26,362 | 37.17 s |
| Three-Point Lighting Study | `04_lighting_study/three_point_lighting_study.blend` | `04_lighting_study/beauty_soft.png`, `beauty_dramatic.png`, `beauty_cool.png` | 11,214 | 26.21 / 27.27 / 27.99 s |
| Procedural Cable and Connector Kit | `05_procedural_cable_kit/procedural_cable_connector_kit.blend` | `05_procedural_cable_kit/beauty.png` | 15,698 | 25.81 s |

Per-project `metrics.json` files record Blender version, render engine, resolution, sample count, evaluated mesh totals, output names, and elapsed render time. `generate_blender_projects.py` contains the procedural scene-building script.
