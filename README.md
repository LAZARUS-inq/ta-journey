# ta-journey 🎮

My personal learning path to becoming a **Junior Technical Artist** in the game industry.

This repository contains all tools, scripts, shaders, and notes created during my TA training.

> **Stack:** 3ds Max · Unreal Engine 5 · MAXScript · Python · HLSL

---

## 📁 Structure

```
ta-journey/
├── maxscript/        # Automation tools for 3ds Max
├── shaders/          # HLSL / GLSL shader experiments
├── python/           # Pipeline automation scripts
└── notes/            # Book notes & learning references
```

---

## 🛠️ Tools & Scripts

### MAXScript
| Script | Description |
|---|---|
| `rename_objects.ms` | Renames selected objects to `SM_Object_001` format |
| `reset_pivot.ms` | Resets pivot to center of bounding box |
| `batch_export.ms` | Batch FBX export with validation |

### Python
| Script | Description |
|---|---|
| `rename_pipeline.py` | Asset validation + rename pipeline with JSON report |
| `asset_manager.py` | AssetManager class — scan, fix, report pipeline |
| `maxscript_pipeline.py` | pymxs API — rename + JSON report inside 3ds Max |
| `texture_checker.py` | UE5 Python — texture naming validator + auto-rename with JSON report |
| `material_audit.py` | UE5 Python — full material audit: broken textures, naming violations, duplicates + JSON report |
| `mesh_validator.ms` | 3ds Max MAXScript — pre-export mesh validator: naming, pivot, scale, UV, modifiers, polycount + Dry Run / Fix Mode |
| `mesh_validator.py` | UE5 Python — post-import mesh validator: naming, LOD, lightmap UV, collision, triangles, Nanite + JSON report |

---

## 🎨 Portfolio

| Project | Description | Link |
|---|---|---|
| Hologram Shader | Fresnel + Panner + Sine animation — UE5 | [ArtStation](https://www.artstation.com/artwork/qJqm3N) |
| Water Shader | Dual Panner + Sine waves + Fresnel — UE5 | [ArtStation](https://www.artstation.com/artwork/y4dVL3) |
| Fire Dissolve Shader | Noise + Emissive glow + Blueprint animation — UE5 | [ArtStation](https://www.artstation.com/artwork/2BA2rY) |
| Magic VFX | Niagara particle system with custom material — UE5 | [ArtStation](https://www.artstation.com/artwork/V2wz15) |
| LOD & ISM Optimization | LOD system + Instanced Static Mesh — UE5 | [ArtStation](https://www.artstation.com/artwork/lGJkwO) |
| Snow Accumulation Shader | World Aligned Blend + Niagara VFX — UE5 | [ArtStation](https://www.artstation.com/artwork/kNgqB6) |
| UE5 Python Texture Checker | Texture naming validator + auto-rename pipeline tool | [ArtStation](https://www.artstation.com/artwork/zxbdPw) |
| Wet Surface Shader | Fresnel + Ripples + Puddles + Niagara Rain — UE5 | [ArtStation](https://www.artstation.com/artwork/L4LAkK) |
| UE5 Material Audit Tool | Full material audit — broken textures, naming violations, duplicates + JSON report | [ArtStation](https://www.artstation.com/artwork/lGg1YV) |
| Decal System | Dirt, damage and wetness deferred decals with animated drying cycle — UE5 | [ArtStation](https://www.artstation.com/artwork/Ezra32) |
| Mesh Validator | Two-stage pipeline tool — 3ds Max pre-export + UE5 post-import validation | [ArtStation](https://www.artstation.com/artwork/x3ld8r) |
| Destruction Material | Dynamic crack shader with Emissive glow + Blueprint Timeline animation — UE5 | [ArtStation](https://www.artstation.com/artwork/qJ4NL2) |

---

## 🎓 Certifications

| Certificate | Institution | Date |
|---|---|---|
| Introduction to C++ Programming and Unreal | University of Colorado / Coursera | Oct 2025 |
| More C++ Programming and Unreal | University of Colorado / Coursera | Nov 2025 |

---

## 📚 Learning Resources

### Books
- **The Art of Game Design** — Jesse Schell
- **Game Programming Patterns** — Robert Nystrom *(free: [gameprogrammingpatterns.com](https://gameprogrammingpatterns.com))*
- **The Book of Shaders** — Patricio Gonzalez Vivo *(free: [thebookofshaders.com](https://thebookofshaders.com))*
- **Game Development Patterns with Unreal Engine 5** — Butler & Oliver
- **Game Engine Architecture** — Jason Gregory
- **Real-Time Rendering** — Akenine-Möller

### Online
- [dev.epicgames.com](https://dev.epicgames.com/community/learning) — Unreal Engine official courses
- [tech-artists.org](https://tech-artists.org) — TA community
- [learnpython.org](https://learnpython.org) — Python basics

---

## 🗺️ Roadmap

### Month 1 — Scripting & 3D Foundation
- [x] `rename_objects.ms` — batch rename selected objects
- [x] `reset_pivot.ms` — reset pivot to bounding box center
- [x] `batch_export.ms` — FBX batch export with validation
- [x] Python basics — functions, loops, validation, JSON, os
- [x] `rename_pipeline.py` — asset validation + rename pipeline
- [x] `asset_manager.py` — AssetManager class, scan/fix/report pipeline
- [x] `maxscript_pipeline.py` — pymxs API, rename + JSON report inside 3ds Max

### Month 2 & 3 — Unreal Engine 5 & Shaders
- [x] Material Editor fundamentals
- [x] Hologram shader — Fresnel + Panner + Sine animation
- [x] Water shader — dual Panner + Sine waves + Fresnel
- [x] Fire Dissolve shader — Noise + Emissive glow + Blueprint animation
- [x] Magic VFX — Niagara particle system with custom material
- [x] 3ds Max → FBX → UE5 pipeline

### Month 4 — Optimization & Advanced Shaders
- [x] LOD setup in UE5 — 4 levels, 2x polygon reduction per level
- [x] Mesh LOD Coloration — viewport visualization of LOD distances
- [x] ISM optimization — 858 → 373 Draw Calls (-57%), 50.8K → 7952 Prims (-85%)
- [x] Snow Accumulation shader — World Aligned Blend + MPC animation
- [x] Niagara snowfall VFX — custom particle system built from scratch
- [x] `texture_checker.py` — UE5 Python naming validator + auto-fix + JSON report
- [x] Wet Surface shader — Fresnel + Ripples + Puddles + Niagara Rain
- [ ] Profiling with Unreal Insights

### Month 5 — Pipeline Tools & Portfolio
- [x] `material_audit.py` — UE5 Python full material audit tool (AssetRegistry + MaterialEditingLibrary)
- [x] Decal System — Dirt, Damage, Wetness deferred decals with Fresnel, Normal maps, animated drying cycle + Blueprint Timeline
- [x] `mesh_validator.ms` + `mesh_validator.py` — two-stage mesh validation pipeline (3ds Max + UE5)
- [x] Destruction Material — dynamic crack shader with Emissive glow + Blueprint Timeline + MPC
- [x] ArtStation profile with 12+ projects
- [ ] Asset Dependency Checker — UE5 Python dependency graph via AssetRegistry
- [ ] First job applications

---

## 👤 Author

**LAZARUS-inq**
- GitHub: [@LAZARUS-inq](https://github.com/LAZARUS-inq)
- ArtStation: [artstation.com/lazarus-inq](https://www.artstation.com/lazarus-inq)
- Background: C++ / C# / 3ds Max / Python / Unreal Engine 5
- Goal: Junior Technical Artist at a game studio
